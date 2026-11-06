import requests
from bs4 import BeautifulSoup
import json
import random
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models import SessionLocal, Job, Skill
from nlp.skill_extractor import skill_extractor, SKILL_TAXONOMY
from scraper.seed_data import SEED_JOBS

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 JobMarketAnalyzer/1.0'
}

class JobCollector:
    """
    Multi-source Job Collector handling permitted API feeds,
    HTML scraping via BeautifulSoup, and dynamic live job stream ingestion.
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_from_remoteok(self, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Fetches live tech job postings from RemoteOK public JSON API.
        """
        collected = []
        try:
            url = "https://remoteok.com/api"
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                # Skip first legal notice element
                postings = [p for p in data if isinstance(p, dict) and p.get('position')][:limit]
                
                for item in postings:
                    title = item.get('position', 'Software Developer')
                    company = item.get('company', 'Tech Company')
                    description = item.get('description', '')
                    tags = item.get('tags', [])
                    url = item.get('url', '')
                    
                    # Clean HTML tags from description with BeautifulSoup
                    soup = BeautifulSoup(description, 'html.parser')
                    clean_desc = soup.get_text(separator=' ').strip()
                    if tags:
                        clean_desc += f" Required skills and keywords: {', '.join(tags)}."

                    # Parse or estimate salary if provided
                    salary_min = item.get('salary_min') or None
                    salary_max = item.get('salary_max') or None
                    
                    collected.append({
                        'title': title,
                        'company': company,
                        'location': item.get('location') or 'Remote',
                        'work_mode': 'Remote',
                        'experience_level': self._infer_experience_level(title, clean_desc),
                        'role_category': self._infer_role_category(title, clean_desc),
                        'min_salary': float(salary_min) if salary_min else None,
                        'max_salary': float(salary_max) if salary_max else None,
                        'currency': 'USD',
                        'description': clean_desc,
                        'url': url,
                        'source': 'RemoteOK API',
                        'posted_date': datetime.utcnow()
                    })
        except Exception as e:
            print(f"[RemoteOK API] Note: {e} - Falling back to local permitted feeds.")

        return collected

    def fetch_from_arbeitnow(self, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Fetches live tech job postings from Arbeitnow public job board API.
        """
        collected = []
        try:
            url = "https://www.arbeitnow.com/api/job-board-api"
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                postings = data.get('data', [])[:limit]

                for item in postings:
                    title = item.get('title', 'Developer')
                    company = item.get('company_name', 'Tech Corp')
                    desc_html = item.get('description', '')
                    soup = BeautifulSoup(desc_html, 'html.parser')
                    clean_desc = soup.get_text(separator=' ').strip()
                    tags = item.get('tags', [])
                    if tags:
                        clean_desc += f" Technologies: {', '.join(tags)}."

                    is_remote = item.get('remote', False)
                    location = item.get('location', 'Global')
                    
                    collected.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'work_mode': 'Remote' if is_remote else 'Hybrid',
                        'experience_level': self._infer_experience_level(title, clean_desc),
                        'role_category': self._infer_role_category(title, clean_desc),
                        'min_salary': None,
                        'max_salary': None,
                        'currency': 'USD',
                        'description': clean_desc,
                        'url': item.get('url', ''),
                        'source': 'Arbeitnow API',
                        'posted_date': datetime.utcnow()
                    })
        except Exception as e:
            print(f"[Arbeitnow API] Note: {e}")

        return collected

    def generate_synthetic_stream(self, count: int = 15) -> List[Dict[str, Any]]:
        """
        Generates realistic modern job postings with diverse tech stacks (LLMs, Python, Django, SQL, etc.)
        to dynamically simulate live streaming market batches on demand.
        """
        companies = [
            "DataWave AI", "CloudSphere", "NeuralCore Systems", "FinTech Labs", 
            "QuantMatrix", "Apex Logistics", "OmniCloud Tech", "Velocity Robotics", 
            "SaaSify Global", "CyberShield Network", "HealthBridge AI", "HyperScale Computing"
        ]
        
        templates = [
            {
                "title": "{level} Python & Django Software Engineer",
                "role": "Backend Developer",
                "desc": "Seeking a talented engineer to build scalable web applications. Core requirements: Python, Django, PostgreSQL, and SQL optimization. You will build high-speed REST APIs and Dockerize services.",
                "salary_base": (110000, 150000)
            },
            {
                "title": "{level} Machine Learning & LLM Engineer",
                "role": "Machine Learning Engineer",
                "desc": "Join our AI engineering team. Work with PyTorch, LLMs, LangChain, and Generative AI. Requires strong Python, Pandas, NumPy, and vector databases on AWS or GCP.",
                "salary_base": (135000, 195000)
            },
            {
                "title": "{level} Full Stack Developer (React / Python)",
                "role": "Full Stack Developer",
                "desc": "Build delightful interactive customer products. Tech stack: React, TypeScript, Next.js, Python, Flask or FastAPI, SQL, and Docker. Experience with CI/CD is a plus.",
                "salary_base": (105000, 145000)
            },
            {
                "title": "{level} Cloud & DevOps Engineer",
                "role": "DevOps Engineer",
                "desc": "Maintain 99.99% uptime for multi-cluster environments. Core skills: Kubernetes, Docker, Terraform, AWS, Linux, and CI/CD pipelines. Scripting in Python or Go.",
                "salary_base": (125000, 170000)
            },
            {
                "title": "{level} Data Scientist & BI Analyst",
                "role": "Data Scientist",
                "desc": "Analyze petabyte-scale data models. Strong expertise in SQL, Python, Pandas, Scikit-learn, Tableau, and Machine Learning predictive modeling.",
                "salary_base": (115000, 160000)
            }
        ]

        levels = ["Junior", "Mid-Level", "Senior", "Lead"]
        level_map = {
            "Junior": "Entry Level",
            "Mid-Level": "Mid Level",
            "Senior": "Senior Level",
            "Lead": "Lead"
        }
        multiplier = {
            "Junior": 0.7,
            "Mid-Level": 1.0,
            "Senior": 1.35,
            "Lead": 1.6
        }

        modes = ["Remote", "Hybrid", "Onsite"]
        locations = ["San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA", "London, UK", "Bengaluru, India", "Toronto, Canada", "Berlin, Germany"]

        generated = []
        for _ in range(count):
            tpl = random.choice(templates)
            lvl = random.choice(levels)
            comp = random.choice(companies)
            loc = random.choice(locations)
            mode = random.choice(modes)
            
            base_min, base_max = tpl["salary_base"]
            mult = multiplier[lvl]
            min_sal = round((base_min * mult) / 1000) * 1000
            max_sal = round((base_max * mult) / 1000) * 1000
            
            title = tpl["title"].replace("{level}", lvl)
            
            generated.append({
                'title': title,
                'company': comp,
                'location': loc,
                'work_mode': mode,
                'experience_level': level_map[lvl],
                'role_category': tpl["role"],
                'min_salary': float(min_sal),
                'max_salary': float(max_sal),
                'currency': 'USD',
                'description': f"{tpl['desc']} We foster an inclusive environment with competitive benefits, equity, and flexible hours.",
                'url': f"https://{comp.lower().replace(' ', '')}.example.com/careers/{random.randint(1000, 9999)}",
                'source': 'Live Stream Ingestion',
                'posted_date': datetime.utcnow() - timedelta(days=random.randint(0, 5))
            })

        return generated

    def _infer_experience_level(self, title: str, text: str) -> str:
        t = f"{title} {text}".lower()
        if any(w in t for w in ['lead', 'principal', 'staff', 'head of', 'architect', 'director']):
            return 'Lead'
        if any(w in t for w in ['senior', 'sr.', 'sr ', 'experienced', '5+ years', '7+ years']):
            return 'Senior Level'
        if any(w in t for w in ['junior', 'jr.', 'jr ', 'entry', 'intern', 'graduate', '0-2 years']):
            return 'Entry Level'
        return 'Mid Level'

    def _infer_role_category(self, title: str, text: str) -> str:
        t = f"{title} {text}".lower()
        if any(w in t for w in ['machine learning', 'ml engineer', 'ai engineer', 'deep learning', 'llm']):
            return 'Machine Learning Engineer'
        if any(w in t for w in ['data scientist', 'data science']):
            return 'Data Scientist'
        if any(w in t for w in ['data analyst', 'business intelligence', 'bi analyst']):
            return 'Data Analyst'
        if any(w in t for w in ['devops', 'site reliability', 'sre', 'infrastructure', 'platform engineer']):
            return 'DevOps Engineer'
        if any(w in t for w in ['cloud architect', 'solutions architect']):
            return 'Cloud Architect'
        if any(w in t for w in ['full stack', 'fullstack', 'full-stack']):
            return 'Full Stack Developer'
        if any(w in t for w in ['frontend', 'front end', 'front-end', 'ui engineer', 'react developer']):
            return 'Frontend Developer'
        if any(w in t for w in ['backend', 'back end', 'back-end', 'python developer', 'django developer', 'api engineer']):
            return 'Backend Developer'
        return 'Software Engineer'

    def ingest_to_db(self, jobs_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Saves job postings into the SQLAlchemy database,
        automatically extracting skills for each job and linking them.
        """
        session = SessionLocal()
        new_jobs_count = 0
        new_skills_count = 0

        try:
            # Pre-cache existing skills
            skill_cache = {s.name: s for s in session.query(Skill).all()}

            for item in jobs_data:
                # Deduplication check by company and title
                existing = session.query(Job).filter(
                    Job.title == item['title'],
                    Job.company == item['company']
                ).first()

                if existing:
                    continue

                min_s = item.get('min_salary')
                max_s = item.get('max_salary')
                avg_s = None
                if min_s and max_s:
                    avg_s = round((min_s + max_s) / 2.0, 2)
                elif min_s:
                    avg_s = float(min_s)
                elif max_s:
                    avg_s = float(max_s)

                job = Job(
                    title=item['title'],
                    company=item['company'],
                    location=item.get('location', 'Remote'),
                    work_mode=item.get('work_mode', 'Remote'),
                    experience_level=item.get('experience_level', 'Mid Level'),
                    role_category=item.get('role_category', 'Software Engineer'),
                    min_salary=min_s,
                    max_salary=max_s,
                    avg_salary=avg_s,
                    currency=item.get('currency', 'USD'),
                    description=item.get('description', ''),
                    url=item.get('url', ''),
                    source=item.get('source', 'Collected'),
                    posted_date=item.get('posted_date', datetime.utcnow())
                )
                session.add(job)

                # Extract skills using NLP engine
                text_to_scan = f"{job.title} {job.description}"
                extracted_skills = skill_extractor.extract_skills(text_to_scan)

                for sk in extracted_skills:
                    sk_name = sk['name']
                    if sk_name not in skill_cache:
                        new_skill = Skill(
                            name=sk_name,
                            category=sk['category']
                        )
                        session.add(new_skill)
                        session.flush()
                        skill_cache[sk_name] = new_skill
                        new_skills_count += 1
                    
                    job.skills.append(skill_cache[sk_name])

                new_jobs_count += 1

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error during job ingestion: {e}")
            raise e
        finally:
            session.close()

        return {
            'new_jobs': new_jobs_count,
            'new_skills': new_skills_count
        }

    def seed_initial_data(self) -> Dict[str, int]:
        """Seeds the database with initial rich tech jobs if empty."""
        session = SessionLocal()
        count = session.query(Job).count()
        session.close()

        if count == 0:
            print("[Seed] Initializing database with seed job postings...")
            # Combine core seed jobs and initial synthetic stream
            all_seed = SEED_JOBS + self.generate_synthetic_stream(count=20)
            return self.ingest_to_db(all_seed)
        return {'new_jobs': 0, 'new_skills': 0}

# Global collector instance
job_collector = JobCollector()
