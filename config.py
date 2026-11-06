import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'job-market-intelligence-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(DATA_DIR, 'job_market.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RAW_DATA_PATH = os.path.join(DATA_DIR, 'raw_jobs.json')
    PROCESSED_DATA_PATH = os.path.join(DATA_DIR, 'processed_jobs.csv')
    
    # Predefined target roles for intelligence analysis
    TARGET_ROLES = [
        "Backend Developer",
        "Frontend Developer",
        "Full Stack Developer",
        "Data Scientist",
        "Machine Learning Engineer",
        "DevOps Engineer",
        "Cloud Architect",
        "Data Analyst"
    ]
