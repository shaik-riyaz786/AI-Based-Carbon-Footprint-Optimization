from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import FileField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import shap
import numpy as np
import pandas as pd
import joblib
import xgboost as xgb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import io
import base64
import google.generativeai as genai
import re
import warnings
import logging  # Added for better error logging

# Set logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend; must be FIRST
import matplotlib.pyplot as plt

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:@localhost:3307/carbon_db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Custom validator for password
def validate_password(form, field):
    password = field.data
    if len(password) < 6:
        raise ValidationError('Password must be at least 6 characters long.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z0-9]', password):
        raise ValidationError('Password must contain at least one lowercase letter or number.')

# Custom validator for mobile number
def validate_mobile(form, field):
    mobile = field.data
    if not re.match(r'^\d{10}$', mobile):
        raise ValidationError('Mobile number must be exactly 10 digits.')

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        validate_password,
        Regexp(r'^[a-zA-Z0-9@_-]+$', message='Password can only contain alphanumeric characters, @, _, or -.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    mobile = StringField('Mobile Number', validators=[DataRequired(), validate_mobile])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    file = FileField('file', validators=[DataRequired()])

# Gemini Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found.")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# **MODIFIED** Function to generate the report with RELATIVE PATHS
def generate_report(file):
    try:
        # Get the absolute path of the current script directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct RELATIVE paths to the model files
        preprocessor_path = os.path.join(current_dir, 'preprocessing_weights', 'Preprocessor.pkl')
        xgb_model_path = os.path.join(current_dir, 'Model_weights', 'xgboost_model.pkl')
        
        # Verify files exist (for debugging)
        if not os.path.exists(preprocessor_path):
            raise FileNotFoundError(f"Preprocessor.pkl not found at: {preprocessor_path}")
        if not os.path.exists(xgb_model_path):
            raise FileNotFoundError(f"xgboost_model.pkl not found at: {xgb_model_path}")
        
        logger.info(f"Loading preprocessor from: {preprocessor_path}")
        logger.info(f"Loading model from: {xgb_model_path}")
        
        # Load the files
        preprocessor = joblib.load(preprocessor_path)
        xgb_model = joblib.load(xgb_model_path)

        # Read the file directly into a DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            return None, None, None, "Unsupported file format."

        original_df = df.copy()

        df['Timestamp_Date'] = pd.to_datetime(df['Timestamp_Date'], errors='coerce')
        
        if df['Timestamp_Date'].isna().any():
            print("Warning: Some dates could not be parsed.")
        df = df.sort_values('Timestamp_Date').reset_index(drop=True)
        
        
        df['Temperature_Control'] = df['Temperature_Control'].map({'TRUE': 1, 'FALSE': 0, True: 1, False: 0})
        df['Year'] = df['Timestamp_Date'].dt.year
        df['Month'] = df['Timestamp_Date'].dt.month
        df['Day'] = df['Timestamp_Date'].dt.day
        df = df.drop(['Timestamp_Date'], axis=1, errors='ignore')

        if 'CO₂e_Total' not in df.columns:
            df['CO₂e_Total'] = np.nan
            original_df['CO₂e_Total'] = np.nan

        predicted_data = None
        if df['CO₂e_Total'].isna().all():
            X = df.drop(columns=['CO₂e_Total'])
            X_processed = preprocessor.transform(X)
            predictions = xgb_model.predict(X_processed)
            df['CO₂e_Total'] = predictions
            original_df['CO₂e_Total'] = predictions

            predicted_data = original_df.to_dict(orient='records')

        X = df.drop(columns=['CO₂e_Total'])
        y = df['CO₂e_Total']
        X_processed = preprocessor.transform(X)

        def get_feature_names(preprocessor, X):
            numeric_features = preprocessor.transformers_[0][1].named_steps['scaler'].get_feature_names_out()
            categorical_features = preprocessor.transformers_[1][1].named_steps['onehot'].get_feature_names_out()
            return np.concatenate([numeric_features, categorical_features])

        feature_names = get_feature_names(preprocessor, X)

        X_train, X_temp, y_train, y_temp = train_test_split(X_processed, y, test_size=0.3, random_state=42)
        X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
        X_sample = X_test

        explainer = shap.TreeExplainer(xgb_model)
        shap_values = explainer.shap_values(X_sample)

        plt.figure(figsize=(12, 8))
        shap.summary_plot(shap_values, X_sample, feature_names=feature_names, plot_type="bar", 
                          show=False, color='#4CAF50', max_display=10)
        plt.title("SHAP Feature Importance\n(Bar Length Indicates Mean Absolute Impact)", fontsize=16, pad=20, fontweight='bold')
        plt.xlabel("Mean Absolute SHAP Value", fontsize=12)
        plt.ylabel("Features", fontsize=12)
        plt.grid(True, axis='x', linestyle='--', alpha=0.3)
        plt.legend(['Feature Importance'], loc='lower right', fontsize=10)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.gcf().savefig(buf, format='png', bbox_inches='tight', dpi=150)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        def generate_esg_summary_with_gemini(shap_values, feature_names):
            feature_importance = np.abs(shap_values).mean(axis=0)
            sorted_idx = np.argsort(feature_importance)[::-1]
            top_features_str = "Top Contributing Features to CO₂ Emissions:\n"
            for i in sorted_idx[:10]:
                top_features_str += f"{feature_names[i]}: {feature_importance[i]:.4f}\n"
            prompt = f"""
            You are an ESG expert. Based on the following feature importance:

            {top_features_str}

            Generate a comprehensive ESG summary report. Include:
            1. Overview of key drivers.
            2. ESG risk hotspots.
            3. Actionable recommendations.
            4. Sustainability strategies.

            Professional, concise, structured with headings. No Markdown symbols.
            """
            response = model.generate_content(prompt)
            cleaned_text = re.sub(r'[#*]+', '', response.text)
            return cleaned_text

        esg_summary = generate_esg_summary_with_gemini(shap_values, feature_names)
        return esg_summary, image_base64, predicted_data, None

    except FileNotFoundError as e:
        logger.error(f"Model file not found: {str(e)}")
        return None, None, None, f"Model file missing: {str(e)}. Ensure 'preprocessing_weights' and 'Model_weights' directories are in the app root."
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return None, None, None, str(e)

# Routes (unchanged)
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_user and existing_email:
            flash('Both username and email are already in Database, please try different username and Email', 'error')
            return redirect(url_for('register'))
        elif existing_user:
            flash('Username already registered, please try different username', 'error')
            return redirect(url_for('register'))
        elif existing_email:
            flash('Email already registered, please try different Email', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password, mobile=form.mobile.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UploadForm()
    esg_summary = ""
    image_base64 = ""
    predicted_data = None

    if form.validate_on_submit():
        file = form.file.data
        if file and file.filename.endswith(('.csv', '.xlsx', '.xls')):
            esg_summary, image_base64, predicted_data, error = generate_report(file)
            if error:
                flash(error, 'error')
            else:
                flash('Report generated successfully!', 'success')
        else:
            flash('Invalid file format.', 'error')

    return render_template('dashboard.html', form=form, esg_summary=esg_summary, image_base64=image_base64, predicted_data=predicted_data)

@app.route('/model_comparison')
@login_required
def model_comparison():
    return render_template('model_comparison.html')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)