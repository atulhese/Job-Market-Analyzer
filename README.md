# ⚡ Job Market Intelligence & Skill Trend Analyzer

A comprehensive data analytics platform and web application that extracts, preprocesses, and visualizes live technical hiring trends, compensation premiums, and in-demand skills from job descriptions, featuring an intelligent career skill gap recommender.

---

## 🎯 Problem Statement
Job seekers and engineering students frequently struggle to identify which technical skills actually command high hiring demand and premium compensation. Many candidates invest months learning outdated tools without understanding the specific tech stacks requested by modern software teams.

---

## ✨ Features & Architecture

### 1. 🌐 Multi-Source Data Collection
- **Permitted Web Scraping & APIs**:
  - Connects to developer job APIs (RemoteOK, Arbeitnow) and extracts structured attributes.
  - HTML content scraping with `BeautifulSoup` to clean HTML entities and parse technical descriptions.
  - Live streaming data generator to simulate and inject fresh market batches on demand.
  - Automatic deduplication and persistent storage via `SQLAlchemy`.

### 2. 🧠 NLP Technical Skill Extraction
- **Comprehensive Skill Taxonomy**:
  - Automatically identifies skills across **Languages** (Python, TypeScript, Go, Java, C++, Rust), **Web & Backend** (Django, Flask, FastAPI, React, Next.js, Node.js), **Databases** (SQL, PostgreSQL, MySQL, MongoDB, Redis), **AI / ML** (LLMs, Machine Learning, PyTorch, LangChain, Generative AI, Pandas, NumPy), and **Cloud & DevOps** (AWS, Docker, Kubernetes, Terraform, CI/CD).
  - Handles tokenization, case-insensitive word-boundaries, and aliases (e.g. `k8s` ➔ `Kubernetes`, `react.js` ➔ `React`, `postgres` ➔ `PostgreSQL`).

### 3. 🐼 Data Cleaning & Preprocessing (Pandas & NumPy)
- Imputes missing salary ranges using median compensation grouped by role and experience level.
- Normalizes compensation into standardized annual USD figures (`min_salary`, `max_salary`, `avg_salary`).
- Categorizes experience tiers (`Entry Level`, `Mid Level`, `Senior Level`, `Lead`) and work modes (`Remote`, `Hybrid`, `Onsite`).
- Exports clean processed snapshots to CSV for auditing.

### 4. 📊 Statistical Market Analysis & Interactive Dashboards
- **Executive Dashboard**:
  - KPI Cards: Total Jobs Analyzed, Unique Skills Tracked, Mean Annual Salary, Remote Share %.
  - Interactive **Chart.js** visualizations:
    - *Top In-Demand Skills* (Horizontal Bar Chart)
    - *Highest Paying Technical Skills* vs Market Benchmark
    - *Work Mode Distribution* (Doughnut Chart)
    - *Experience Level Compensation Curve* (Progression Bar)
  - Dynamic Role Filter to drill down into specific positions (e.g., *Backend Developer*, *ML Engineer*, *Full Stack Developer*).

### 5. 🎯 Skill Matrix & Co-Occurrence Intelligence
- Searchable benchmark table showing job mention count, average salary, and salary premium percentage (e.g., *LLMs: +38.5% above market average*).
- Interactive **Skill Co-Occurrence Finder**: Select any base skill (e.g. `Python`) to instantly see which complementary skills appear alongside it most frequently (e.g., `SQL` 72%, `Docker` 55%, `Django` 45%).

### 6. 🚀 Career Skill Gap & Roadmap Recommender
- Input your current skills (or paste your resume / target job description) and select a target dream role.
- Computes:
  - **Match Score %** (Profile readiness).
  - **Skills You Have** (with validated checkmarks).
  - **High-ROI Missing Skills** (ranked by frequency and average salary).
  - **Estimated Compensation Uplift** (potential annual salary increase).
  - **Personalized 4-Week Actionable Roadmap** with weekly milestones and a capstone project deliverable.

---

## 🛠️ Technology Stack
- **Data Engineering**: Python 3, Pandas, NumPy
- **Extraction & Scraping**: BeautifulSoup4, Requests, Regex NLP Tokenizer
- **Backend**: Flask, SQLAlchemy, SQLite (with optional PostgreSQL support)
- **Frontend / Visualization**: HTML5, CSS3 Glassmorphism, JavaScript, Chart.js

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Access the Dashboard
Open your browser and navigate to:
👉 **`http://127.0.0.1:5050`**

---

## 📁 Project Directory Structure
```
job-market-analyzer/
├── app.py                      # Flask web server & REST API endpoints
├── config.py                   # App configuration & database paths
├── models.py                   # SQLAlchemy schema (Jobs, Skills, Associations)
├── requirements.txt           # Python dependencies
├── README.md                  # Documentation & architecture guide
├── data/
│   ├── job_market.db          # SQLite persistent database
│   └── processed_jobs.csv     # Cleaned Pandas dataset export
├── scraper/
│   ├── job_collector.py       # API collector, BeautifulSoup scraper & generator
│   └── seed_data.py           # Comprehensive seed dataset of tech postings
├── nlp/
│   ├── skill_extractor.py     # Skill taxonomy & regex extraction engine
│   └── recommender.py         # Match score, gap analysis & 4-week roadmap generator
├── analytics/
│   └── data_pipeline.py       # Pandas data cleaning, imputation & aggregations
├── static/
│   ├── css/
│   │   └── styles.css         # Dark modern analytics UI design system
│   └── js/
│       ├── dashboard.js       # Chart.js charts and dynamic role filtering
│       └── recommender.js     # Presets and interactive recommender helpers
└── templates/
    ├── base.html              # Layout, navbar, and status banners
    ├── index.html             # Executive analytics dashboard
    ├── jobs.html              # Job explorer with search, filters & JD modal
    ├── skills.html            # Skill matrix & co-occurrence finder
    ├── recommender.html       # Skill gap analyzer & career roadmap
    └── scraper.html           # Scraper & pipeline control center
```
