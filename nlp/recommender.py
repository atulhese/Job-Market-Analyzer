from typing import List, Dict, Any, Optional
import pandas as pd
from nlp.skill_extractor import skill_extractor, SKILL_TAXONOMY
from analytics.data_pipeline import data_pipeline

class SkillRecommender:
    """
    Intelligent Career & Skill Gap Analyzer that compares candidate
    skills against live job market demand and formulates an actionable roadmap.
    """

    def analyze_gap(
        self, 
        user_skills_input: str = "",
        resume_text: str = "",
        target_role: str = "Backend Developer",
        custom_job_description: str = ""
    ) -> Dict[str, Any]:
        """
        Executes end-to-end skill gap analysis and generates tailored recommendations.
        """
        # 1. Extract candidate's skills from input or resume
        combined_user_text = f"{user_skills_input} {resume_text}"
        user_skills = set(skill_extractor.extract_skill_names(combined_user_text))

        # 2. Determine target requirements
        if custom_job_description.strip():
            # Match directly against the provided job description
            required_skills_list = skill_extractor.extract_skill_names(custom_job_description)
            target_title = "Custom Job Description"
        else:
            # Match against market demand for the selected role
            top_role_skills = data_pipeline.get_top_demanded_skills(limit=12, role_filter=target_role)
            required_skills_list = [item['skill'] for item in top_role_skills]
            target_title = target_role

        required_skills = set(required_skills_list)
        if not required_skills:
            # Fallback benchmark if no specific skills found
            required_skills = {"Python", "SQL", "Git", "Docker", "REST APIs"}

        # 3. Compute matching and missing skills
        matched_skills = sorted(list(user_skills.intersection(required_skills)))
        missing_skills = sorted(list(required_skills.difference(user_skills)))

        # 4. Calculate Match Score
        total_req = len(required_skills)
        match_score = round((len(matched_skills) / total_req) * 100) if total_req > 0 else 0

        # 5. Enrich missing skills with market intelligence (Salary & Demand)
        salary_data = {item['skill']: item for item in data_pipeline.get_skill_salary_analysis(min_mentions=1)}
        
        ranked_missing = []
        for s in missing_skills:
            meta = salary_data.get(s, {})
            ranked_missing.append({
                'skill': s,
                'category': SKILL_TAXONOMY.get(s, {}).get('category', 'General'),
                'avg_salary': meta.get('avg_salary', 120000),
                'premium_pct': meta.get('salary_premium_pct', 5.0),
                'demand_frequency': meta.get('job_count', 3)
            })

        # Sort missing skills by demand and salary premium
        ranked_missing.sort(key=lambda x: (x['demand_frequency'], x['avg_salary']), reverse=True)

        # 6. Estimate Potential Salary Uplift
        market_overview = data_pipeline.get_market_overview()
        base_salary = market_overview.get('avg_market_salary', 125000)
        
        # Additional boost calculation
        estimated_boost = 0
        if ranked_missing:
            top_premiums = [m['premium_pct'] for m in ranked_missing[:3] if m['premium_pct'] > 0]
            avg_premium = sum(top_premiums) / len(top_premiums) if top_premiums else 8.5
            estimated_boost = int(base_salary * (avg_premium / 100.0))

        # 7. Generate Personalized 4-Week Skill Roadmap
        roadmap = self._generate_roadmap(matched_skills, [m['skill'] for m in ranked_missing], target_title)

        return {
            'target_title': target_title,
            'match_score': match_score,
            'user_skills': sorted(list(user_skills)),
            'matched_skills': matched_skills,
            'missing_skills': ranked_missing,
            'estimated_salary_boost': estimated_boost,
            'roadmap': roadmap,
            'total_market_required': total_req
        }

    def _generate_roadmap(self, possessed: List[str], missing: List[str], role: str) -> List[Dict[str, Any]]:
        """Constructs an actionable 4-week step-by-step upskilling plan."""
        m1 = missing[0] if len(missing) > 0 else "System Architecture"
        m2 = missing[1] if len(missing) > 1 else "Database Optimization"
        m3 = missing[2] if len(missing) > 2 else "Cloud & CI/CD"
        m4 = missing[3] if len(missing) > 3 else "Production Security"

        return [
            {
                "week": "Week 1",
                "phase": f"Foundation & Core Framework ({m1})",
                "objective": f"Master high-frequency concepts in {m1} and integrate with your existing strengths ({', '.join(possessed[:2]) or 'basics'}).",
                "deliverable": f"Build a clean module or micro-service showcasing idiomatic {m1} patterns."
            },
            {
                "week": "Week 2",
                "phase": f"Data Persistence & Scaling ({m2})",
                "objective": f"Implement efficient queries, indexing, and connection pooling using {m2}.",
                "deliverable": "Design an optimized schema with relational constraints and benchmark query latency."
            },
            {
                "week": "Week 3",
                "phase": f"Containerization & Pipeline Deployment ({m3})",
                "objective": f"Containerize your full application stack with Docker and automate CI/CD testing workflows.",
                "deliverable": "Push image to registry and configure automated deployment workflows."
            },
            {
                "week": "Week 4",
                "phase": f"Full Capstone Portfolio Project ({role} Spec)",
                "objective": f"Tie together {m1}, {m2}, and {m3} into a complete production-grade GitHub portfolio piece.",
                "deliverable": "Live hosted web application demo with comprehensive README, API docs, and architecture diagram."
            }
        ]

# Global recommender instance
skill_recommender = SkillRecommender()
