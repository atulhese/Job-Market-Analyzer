import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from models import SessionLocal, Job, Skill
from config import Config

class DataPipeline:
    """
    Pandas-powered data cleaning, imputation, preprocessing,
    and statistical intelligence engine.
    """

    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.load_and_clean_data()

    def load_and_clean_data(self) -> pd.DataFrame:
        """
        Loads all jobs and associated skills from database,
        executes Pandas data cleaning, imputes missing values,
        and saves processed snapshot.
        """
        session = SessionLocal()
        try:
            jobs = session.query(Job).all()
        except Exception as e:
            self.df = pd.DataFrame()
            return self.df

        try:
            if not jobs:
                self.df = pd.DataFrame()
                return self.df

            records = []
            for j in jobs:
                records.append({
                    'id': j.id,
                    'title': j.title.strip() if j.title else 'Software Engineer',
                    'company': j.company.strip() if j.company else 'Confidential',
                    'location': j.location.strip() if j.location else 'Remote',
                    'work_mode': j.work_mode.strip() if j.work_mode else 'Remote',
                    'experience_level': j.experience_level.strip() if j.experience_level else 'Mid Level',
                    'role_category': j.role_category.strip() if j.role_category else 'Software Engineer',
                    'min_salary': j.min_salary,
                    'max_salary': j.max_salary,
                    'avg_salary': j.avg_salary,
                    'source': j.source or 'Scraped',
                    'posted_date': j.posted_date,
                    'skills': [s.name for s in j.skills]
                })

            df = pd.DataFrame(records)

            # --- Pandas Data Cleaning & Preprocessing ---

            # 1. Clean and standardize work modes
            df['work_mode'] = df['work_mode'].replace({
                'remote': 'Remote',
                'hybrid': 'Hybrid',
                'onsite': 'Onsite',
                'in-office': 'Onsite'
            }).fillna('Remote')

            # 2. Impute missing salaries using median of role + experience level
            # Baseline benchmark if both are missing
            overall_median = 125000.0

            # Calculate grouped medians
            salary_grouped_medians = df.groupby(['role_category', 'experience_level'])['avg_salary'].transform('median')
            df['avg_salary'] = df['avg_salary'].fillna(salary_grouped_medians)
            
            role_medians = df.groupby('role_category')['avg_salary'].transform('median')
            df['avg_salary'] = df['avg_salary'].fillna(role_medians)
            df['avg_salary'] = df['avg_salary'].fillna(overall_median)

            # Round salaries
            df['avg_salary'] = df['avg_salary'].round(2)
            df['min_salary'] = df['min_salary'].fillna(df['avg_salary'] * 0.88).round(2)
            df['max_salary'] = df['max_salary'].fillna(df['avg_salary'] * 1.15).round(2)

            # 3. Add skill counts per job
            df['skill_count'] = df['skills'].apply(len)

            # 4. Save processed snapshot for audits
            df.to_csv(Config.PROCESSED_DATA_PATH, index=False)

            self.df = df
            return self.df
        finally:
            session.close()

    def get_market_overview(self) -> Dict[str, Any]:
        """
        Returns high-level KPI metrics for the executive dashboard.
        """
        if self.df is None or self.df.empty:
            self.load_and_clean_data()
        
        if self.df.empty:
            return {
                'total_jobs': 0,
                'unique_skills': 0,
                'avg_market_salary': 0,
                'median_market_salary': 0,
                'remote_pct': 0,
                'top_skill': 'N/A'
            }

        df = self.df
        total_jobs = len(df)
        
        # Flatten all skills
        all_skills = [s for sublist in df['skills'] for s in sublist]
        unique_skills = len(set(all_skills))
        top_skill = pd.Series(all_skills).value_counts().index[0] if all_skills else 'Python'

        avg_salary = int(df['avg_salary'].mean())
        median_salary = int(df['avg_salary'].median())

        remote_count = len(df[df['work_mode'] == 'Remote'])
        remote_pct = round((remote_count / total_jobs) * 100, 1)

        return {
            'total_jobs': total_jobs,
            'unique_skills': unique_skills,
            'avg_market_salary': avg_salary,
            'median_market_salary': median_salary,
            'remote_pct': remote_pct,
            'top_skill': top_skill
        }

    def get_top_demanded_skills(self, limit: int = 15, role_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Computes top demanded skills, their frequency, and percentage of job postings.
        """
        if self.df is None or self.df.empty:
            self.load_and_clean_data()

        df = self.df
        if role_filter and role_filter != 'All':
            df = df[df['role_category'] == role_filter]

        if df.empty:
            return []

        total_postings = len(df)
        all_skills = [s for sublist in df['skills'] for s in sublist]
        
        skill_series = pd.Series(all_skills).value_counts().head(limit)
        
        result = []
        for skill_name, count in skill_series.items():
            pct = round((count / total_postings) * 100, 1)
            result.append({
                'skill': skill_name,
                'count': int(count),
                'percentage': pct
            })

        return result

    def get_skill_salary_analysis(self, min_mentions: int = 2) -> List[Dict[str, Any]]:
        """
        Analyzes the salary premium for each skill (avg salary for jobs requiring that skill).
        Sorts by highest paying skills first.
        """
        if self.df is None or self.df.empty:
            self.load_and_clean_data()

        df = self.df
        if df.empty:
            return []

        market_avg = df['avg_salary'].mean()

        # Explode skills to row-level
        exploded = df.explode('skills')
        exploded = exploded.dropna(subset=['skills'])

        grouped = exploded.groupby('skills').agg(
            job_count=('id', 'count'),
            avg_salary=('avg_salary', 'mean'),
            median_salary=('avg_salary', 'median'),
            min_salary=('min_salary', 'min'),
            max_salary=('max_salary', 'max')
        ).reset_index()

        # Filter skills with sufficient sample size
        grouped = grouped[grouped['job_count'] >= min_mentions]
        grouped['salary_premium_pct'] = ((grouped['avg_salary'] - market_avg) / market_avg * 100).round(1)
        grouped = grouped.sort_values(by='avg_salary', ascending=False)

        result = []
        for _, row in grouped.iterrows():
            result.append({
                'skill': row['skills'],
                'job_count': int(row['job_count']),
                'avg_salary': int(row['avg_salary']),
                'median_salary': int(row['median_salary']),
                'salary_premium_pct': float(row['salary_premium_pct'])
            })

        return result

    def get_role_distribution(self) -> List[Dict[str, Any]]:
        """Role category counts and average salary by role."""
        if self.df is None or self.df.empty:
            self.load_and_clean_data()

        df = self.df
        if df.empty:
            return []

        grouped = df.groupby('role_category').agg(
            count=('id', 'count'),
            avg_salary=('avg_salary', 'mean')
        ).reset_index().sort_values(by='count', ascending=False)

        return [
            {
                'role': row['role_category'],
                'count': int(row['count']),
                'avg_salary': int(row['avg_salary'])
            }
            for _, row in grouped.iterrows()
        ]

    def get_work_mode_stats(self) -> List[Dict[str, Any]]:
        """Work mode breakdown (Remote, Hybrid, Onsite)."""
        if self.df is None or self.df.empty:
            self.load_and_clean_data()

        df = self.df
        if df.empty:
            return []

        grouped = df.groupby('work_mode').agg(
            count=('id', 'count'),
            avg_salary=('avg_salary', 'mean')
        ).reset_index()

        total = len(df)
        return [
            {
                'mode': row['work_mode'],
                'count': int(row['count']),
                'percentage': round((row['count'] / total) * 100, 1),
                'avg_salary': int(row['avg_salary'])
            }
            for _, row in grouped.iterrows()
        ]

    def get_experience_salary_trends(self) -> List[Dict[str, Any]]:
        """Experience level vs average compensation progression."""
        if self.df is None or self.df.empty:
            self.load_and_clean_data()

        df = self.df
        if df.empty:
            return []

        order = ['Entry Level', 'Mid Level', 'Senior Level', 'Lead']
        grouped = df.groupby('experience_level').agg(
            count=('id', 'count'),
            avg_salary=('avg_salary', 'mean'),
            median_salary=('avg_salary', 'median')
        ).reindex(order).dropna().reset_index()

        return [
            {
                'level': row['experience_level'],
                'count': int(row['count']),
                'avg_salary': int(row['avg_salary']),
                'median_salary': int(row['median_salary'])
            }
            for _, row in grouped.iterrows()
        ]

    def get_skill_cooccurrence(self, target_skill: str, top_n: int = 8) -> List[Dict[str, Any]]:
        """
        Finds skills that most frequently co-occur with the target skill.
        e.g., If a job asks for Python, what other skills are also demanded?
        """
        if self.df is None or self.df.empty:
            self.load_and_clean_data()

        df = self.df
        if df.empty:
            return []

        # Filter jobs containing the target skill
        target_jobs = df[df['skills'].apply(lambda skills: target_skill in skills)]
        if target_jobs.empty:
            return []

        total_target_jobs = len(target_jobs)
        other_skills = [
            s for sublist in target_jobs['skills'] for s in sublist if s != target_skill
        ]

        series = pd.Series(other_skills).value_counts().head(top_n)
        return [
            {
                'skill': s_name,
                'co_count': int(count),
                'co_percentage': round((count / total_target_jobs) * 100, 1)
            }
            for s_name, count in series.items()
        ]

# Global pipeline instance
data_pipeline = DataPipeline()
