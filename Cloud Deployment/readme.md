# Complete Guide: Deploying Your Flask App to Google Cloud Platform (GCP)

This guide provides a **step-by-step walkthrough** for deploying your Flask ESG CO₂ Emissions Analysis app to GCP from scratch. We'll cover everything from creating a GCP account to verifying the deployment. By the end, your app will be live on Google App Engine with a MySQL database on Cloud SQL.

**Assumptions**:
- You have a Google account (Gmail works).
- You have basic command-line knowledge (e.g., using Terminal on macOS/Linux or Command Prompt/PowerShell on Windows).
- Your app code is ready (e.g., `app.py`, templates, model files).
- Estimated time: 1-2 hours for first-timers.

**Prerequisites**:
- Install the [Google Cloud SDK (gcloud CLI)](https://cloud.google.com/sdk/docs/install) on your local machine.
- Python 3.8+ installed locally.
- Git installed (for cloning/version control, optional but recommended).

## Step 1: Create a GCP Account and Project
1. **Sign Up for GCP**:
   - Go to [cloud.google.com](https://cloud.google.com).
   - Click **"Get started for free"** (new users get $300 free credits for 90 days).
   - Sign in with your Google account.
   - Accept the terms and provide billing info (required, but won't charge until credits expire or you exceed limits).

2. **Create a New Project**:
   - In the GCP Console ([console.cloud.google.com](https://console.cloud.google.com)), click the project dropdown at the top.
   - Select **"New Project"**.
   - Enter a project name (e.g., `esg-app-project`). The Project ID will auto-generate (e.g., `esg-app-project-12345` – note this for later).
   - Click **"Create"**.
   - Once created, select it from the dropdown.

3. **Enable Billing**:
   - In the GCP Console sidebar, go to **Billing** > **Link a billing account**.
   - Create or select a billing account and link it to your project.
   - This enables paid services like App Engine and Cloud SQL.

## Step 2: Install and Initialize Google Cloud SDK
1. **Install gcloud CLI**:
   - Download and install from [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install).
   - For macOS: `brew install --cask google-cloud-sdk` (if using Homebrew).
   - For Windows/Linux: Follow the platform-specific instructions.

2. **Initialize gcloud**:
   - Open your terminal/command prompt.
   - Run: `gcloud init`
   - Log in when prompted (opens a browser for authentication).
   - Select your project (e.g., `esg-app-project-12345`).
   - Set your default region (e.g., `asia-south1` for your app).

3. **Verify Installation**:
   ```bash
   gcloud --version
   gcloud config list project
   ```
   - Output should show your project ID.

## Step 3: Enable Required APIs
Your app uses App Engine for hosting and Cloud SQL for the database. Enable these APIs:

1. **In GCP Console**:
   - Go to **APIs & Services** > **Library**.
   - Search for and enable:
     - **App Engine Admin API**
     - **Cloud SQL Admin API**
     - **Cloud Build API** (for deployments)

2. **Via CLI** (alternative):
   ```bash
   gcloud services enable appengine.googleapis.com
   gcloud services enable sqladmin.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

## Step 4: Set Up Cloud SQL (MySQL Database)
Your app connects to a MySQL instance named `mysql123` in `asia-south1`.

1. **Create Cloud SQL Instance**:
   - In GCP Console, go to **SQL** > **Create Instance**.
   - Click **"Choose MySQL"**.
   - **Instance ID**: Enter `mysql123`.
   - **Password**: Set root password to `Mysql@123` (as in your code; use a stronger one in production!).
   - **Region**: `asia-south1`.
   - **Configuration**: Standard (default for starters).
   - Click **"Create"** (takes 5-10 minutes).

2. **Create Database**:
   - Once created, click on `mysql123` > **Databases** tab.
   - Click **"Create Database"**.
   - Database ID: `esg_db`.
   - Charset: `utf8`.
   - Click **"Create"**.

3. **Configure Authorized Networks (for Local Access)**:
   - In the instance overview, go to **Connections** > **Networking** tab.
   - Add your IP: Click **"Add Network"** > Enter `0.0.0.0/0` (allows all; restrict in production) > **Done**.

4. **Note Connection Details**:
   - **Connection Name**: Found in overview (e.g., `your-project-id:asia-south1:mysql123` – matches your code: `crested-analogy-439216-i1:asia-south1:mysql123`).
   - Update your `app.py` if needed to match your actual project ID.

5. **Test Connection (Optional, Local Only)**:
   - Install MySQL client: `pip install mysql-connector-python`.
   - Use Cloud SQL Proxy:
     ```bash
     # Download proxy: wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
     # chmod +x cloud_sql_proxy
     ./cloud_sql_proxy -instances=your-project-id:asia-south1:mysql123=tcp:3306
     ```
   - In another terminal: Connect via `mysql -u root -p -h 127.0.0.1` (password: `Mysql@123`).

## Step 5: Prepare Your App for Deployment
1. **Organize Your Project Directory**:
   ```
   your-app/
   ├── app.py                  # Your main Flask app
   ├── requirements.txt        # List all pip dependencies
   ├── app.yaml                # App Engine config (create this)
   ├── .env                    # Local env vars (not deployed)
   ├── preprocessing_weights/
   │   └── Preprocessor.pkl
   ├── Model_weights/
   │   └── xgboost_model.pkl
   └── templates/
       ├── home.html
       ├── register.html
       ├── login.html
       ├── dashboard.html
       └── model_comparison.html
   ```

2. **Create `requirements.txt`**:
   - Run locally: `pip freeze > requirements.txt`.
   - Edit to include essentials (match your imports):
     ```
     Flask==2.3.3
     Flask-SQLAlchemy==3.0.5
     Flask-Login==0.6.3
     Flask-WTF==1.2.1
     WTForms==3.1.1
     mysql-connector-python==8.2.0
     Werkzeug==3.0.1
     python-dotenv==1.0.0
     joblib==1.3.2
     xgboost==2.0.3
     shap==0.46.0
     numpy==1.25.2
     pandas==2.1.4
     scikit-learn==1.3.2
     matplotlib==3.8.2
     google-generativeai==0.3.2
     gunicorn==21.2.0  # For production WSGI server
     ```

3. **Create `app.yaml`** (App Engine config):
   ```yaml
   runtime: python39
   instance_class: F1  # Free tier; upgrade for more traffic

   # Environment variables (sensitive ones like API keys)
   env_variables:
     GEMINI_API_KEY: "your-gemini-api-key-here"  # Replace with actual key

   # Handlers for routing
   handlers:
   - url: /static
     static_dir: static
   - url: /.*
     script: auto

   # Built-in headers for security
   automatic_scaling:
     min_instances: 1
     max_instances: 10
   ```

4. **Update `app.py` for Production**:
   - Your code uses `os.urandom(24)` for SECRET_KEY – good, but ensure it's set via env var in production:
     ```python
     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24).hex())
     ```
   - Add to `.env`: `SECRET_KEY=your-secret-key`.
   - For database: Your URI uses Unix socket – perfect for App Engine.
   - Replace placeholder project ID in URI with yours: `your-project-id:asia-south1:mysql123`.

5. **Add Model Files**:
   - Ensure `preprocessing_weights/Preprocessor.pkl` and `Model_weights/xgboost_model.pkl` are in place. App Engine will upload them.

6. **Set Environment Variables**:
   - Get your Gemini API key from [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
   - Add to `app.yaml` under `env_variables`.

7. **Test Locally**:
   - Run: `python app.py`.
   - Visit `http://localhost:5000` and test registration/upload.
   - Fix any errors (e.g., model paths).

## Step 6: Deploy to App Engine
1. **Navigate to Project Directory**:
   ```bash
   cd your-app/
   ```

2. **Deploy**:
   ```bash
   gcloud app deploy
   ```
   - It will prompt to choose a region (select `asia-south1`).
   - Type `Y` to continue.
   - Deployment takes 5-10 minutes (builds Docker image, uploads files).

3. **View Deployment Logs**:
   ```bash
   gcloud app logs tail -s default
   ```

## Step 7: Verify and Access Your App
1. **Get App URL**:
   ```bash
   gcloud app browse
   ```
   - Opens `https://your-project-id.appspot.com` in your browser.

2. **Test the App**:
   - Register a user.
   - Log in.
   - Upload a sample CSV/Excel file (ensure it has columns like `Timestamp_Date`, `Temperature_Control`).
   - Check for SHAP plot, ESG summary, and predictions.
   - Verify database: Users should persist across sessions.

3. **Monitor in GCP Console**:
   - **App Engine** > **Dashboard**: View traffic/quotas.
   - **Cloud SQL** > **mysql123** > **Query**: Run `SELECT * FROM user;` to see registered users.
   - **Logs Explorer**: Search for errors (e.g., "Model file not found").

## Step 8: Post-Deployment Management
1. **Custom Domain (Optional)**:
   - Go to **App Engine** > **Custom Domains** > Add mapping (requires DNS verification).

2. **Scaling and Costs**:
   - Free tier: 28 instance hours/day (F1 class).
   - Monitor billing in **Billing** section.
   - Upgrade: Edit `app.yaml` (e.g., `instance_class: B1`) and redeploy.

3. **Updates**:
   - Make code changes, then: `gcloud app deploy`.
   - For DB migrations: Use Flask-Migrate or manual SQL.

4. **Cleanup (If Testing)**:
   - Delete project: **IAM & Admin** > **Settings** > **Shut down**.

## Common Issues and Fixes
- **Permission Denied**: Run `gcloud auth login` again.
- **Database Connection Failed**: Check URI in `app.py` matches connection name; ensure APIs enabled.
- **Model Not Found**: Verify directories/files are uploaded (check in Cloud Storage post-deploy).
- **Gemini API Error**: Confirm key in `app.yaml`; test with `curl` locally.
- **Free Tier Limits**: If exceeded, enable billing alerts.
- **Logs Show Import Errors**: Update `requirements.txt` and redeploy.

## Next Steps
- Add CI/CD with GitHub Actions.
- Secure with HTTPS (automatic on App Engine).
- Scale with multiple regions.
- Integrate more ML models.

If you encounter errors, share the exact message/logs for help. Your app is now live—congrats! 🚀

For official docs: [App Engine Quickstart](https://cloud.google.com/appengine/docs/standard/python3/quickstart), [Cloud SQL for MySQL](https://cloud.google.com/sql/docs/mysql/quickstart).