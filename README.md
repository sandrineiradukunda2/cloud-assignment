# E-Learning University Web App

A simple Flask-based university e-learning starter app that you can run locally or deploy on Render.

## Features
- Home page with available courses
- Student registration and login
- Dashboard for enrolled courses
- Course detail page
- Enrollment system
- Database support with SQLite locally and PostgreSQL on Render

## Project Structure
```text
elearning_university_app/
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
├── static/
│   └── styles.css
└── templates/
    ├── base.html
    ├── home.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    └── course_detail.html
```

## Run Locally
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate it:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
3. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open the browser:
   ```text
   http://127.0.0.1:5000
   ```

## Deploy on Render
1. Upload this project to GitHub.
2. Sign in to Render.
3. Click **New +** and choose **Blueprint** or connect the repo as a **Web Service**.
4. If using `render.yaml`, Render can create the web service and PostgreSQL database for you.
5. After deploy, open your app URL.

## Notes for Your Assignment
- The public web app represents the public tier.
- The Render PostgreSQL database represents the private data tier.
- Render load balances traffic when the web service is scaled to multiple instances.
