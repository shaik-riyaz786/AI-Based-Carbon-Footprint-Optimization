# ESG Carbon Footprint Analysis Dashboard

## Overview
The ESG Carbon Footprint Analysis Dashboard is a Flask-based web application that predicts CO₂ emissions for logistics operations using machine learning (XGBoost) and generates ESG (Environmental, Social, Governance) reports with SHAP feature importance plots and actionable sustainability recommendations powered by Google's Gemini AI.

## Features
- **User Authentication**: Register and log in to access the dashboard.
- **File Upload**: Upload CSV or Excel files to predict CO₂ emissions.
- **Machine Learning**: Uses a pretrained XGBoost model with a preprocessing pipeline.
- **SHAP Analysis**: Visualizes feature importance for CO₂ predictions.
- **ESG Reports**: Generates sustainability summaries and recommendations via Gemini AI.
- **Responsive UI**: Modern, animated dashboard with a video background.

## Prerequisites
- Python 3.10+
- MySQL 8.0+ (running on `localhost:3307`)
- Conda (for environment management)
- Google Gemini API key (for ESG report generation)
- Pretrained ML models (`Preprocessor.pkl` and `xgboost_model.pkl`)

## Setup Instructions


### 1. Set Up Conda Environment
Create and activate a Conda environment:
```bash
conda create -n carbon_footprint_env python=3.10
conda activate carbon_footprint_env
```

### 2. Install Dependencies
Install required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Configure MySQL Database
- Ensure MySQL is running on `localhost:3307`.
- Create a database named `esg_db`:
  ```sql
  CREATE DATABASE esg_db;
  ```
- Update `app.py` with your MySQL credentials if different (default: user=`root`, password=``).

### 5. Set Up Environment Variables
Create a `.env` file in the project root:
```plaintext
GEMINI_API_KEY=your_gemini_api_key_here
```
Obtain a Gemini API key from [Google Cloud](https://cloud.google.com/).

### 6. Prepare ML Models
Place the pretrained models in the correct directories:
- `preprocessing_weights/Preprocessor.pkl`
- `Model_weights/xgboost_model.pkl`

### 7. Run the Application
```bash
python app.py
```
- Access the app at `http://localhost:5000`.
- Register a new user, log in, and upload a CSV/Excel file to generate reports.

## Usage
1. **Register/Login**: Create an account or log in to access the dashboard.
2. **Upload Data**: Upload a CSV or Excel file with columns like `Timestamp_Date`, `Temperature_Control`, etc. The file should either exclude `CO₂e_Total` or have it as empty (`NaN`).
3. **View Results**:
   - **Predicted Data**: Table with predicted CO₂ emissions.
   - **SHAP Plot**: Bar plot showing feature importance.
   - **ESG Summary**: AI-generated report with sustainability insights.

## File Structure
```
├── app.py                    # Main Flask application
├── templates/
│   ├── dashboard.html        # Main dashboard with file upload and results
│   ├── home.html            # Home page
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
├── preprocessing_weights/
│   └── Preprocessor.pkl     # Preprocessing pipeline
├── Model_weights/
│   └── xgboost_model.pkl    # XGBoost model
├── Uploads/                 # Temporary folder for uploaded files
├── static/
│   └── background-video.mp4 # Background video for dashboard
├── .env                     # Environment variables (not tracked)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Notes
- Ensure your input files match the expected format (see `generate_report` in `app.py`).
- The app uses Matplotlib with the 'Agg' backend to avoid Tkinter issues.
- Temporary uploaded files are deleted after processing.
- For production, configure a WSGI server (e.g., Gunicorn) and secure the MySQL connection.

## Troubleshooting
- **Tkinter Errors**: Already mitigated with `matplotlib.use('Agg')` and warning suppression in `app.py`.
- **Database Issues**: Verify MySQL is running and credentials are correct.
- **API Errors**: Ensure the Gemini API key is valid and has sufficient quota.
- **Model Errors**: Confirm model files exist in the specified paths.
