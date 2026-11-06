from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, Table, event
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from config import Config

Base = declarative_base()

# Association table for Many-to-Many relationship between Job and Skill
job_skills = Table(
    'job_skills',
    Base.metadata,
    Column('job_id', Integer, ForeignKey('jobs.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
)

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), default='Remote')
    work_mode = Column(String(50), default='Remote')  # Remote, Hybrid, Onsite
    experience_level = Column(String(50), default='Mid Level')  # Entry Level, Mid Level, Senior Level, Lead
    role_category = Column(String(100), default='Software Engineer')
    
    # Standardized annual USD salary
    min_salary = Column(Float, nullable=True)
    max_salary = Column(Float, nullable=True)
    avg_salary = Column(Float, nullable=True)
    currency = Column(String(10), default='USD')
    
    description = Column(Text, nullable=False)
    url = Column(String(500), nullable=True)
    source = Column(String(100), default='Scraped')
    posted_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    skills = relationship('Skill', secondary=job_skills, back_populates='jobs')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'work_mode': self.work_mode,
            'experience_level': self.experience_level,
            'role_category': self.role_category,
            'min_salary': self.min_salary,
            'max_salary': self.max_salary,
            'avg_salary': self.avg_salary,
            'currency': self.currency,
            'description': self.description,
            'url': self.url,
            'source': self.source,
            'posted_date': self.posted_date.strftime('%Y-%m-%d') if self.posted_date else None,
            'skills': [s.name for s in self.skills]
        }

class Skill(Base):
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), default='General')  # Languages, Frameworks, AI/ML, Databases, DevOps, etc.
    description = Column(String(255), nullable=True)

    jobs = relationship('Job', secondary=job_skills, back_populates='skills')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category
        }

# Database engine and session factory
connect_args = {}
if Config.SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
    connect_args = {
        'timeout': 30,
        'check_same_thread': False
    }

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    echo=False,
    connect_args=connect_args
)

if Config.SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
        except Exception:
            pass
        finally:
            cursor.close()

SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

# Auto-initialize database schema
init_db()
