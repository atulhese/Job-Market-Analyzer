from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
from config import Config
from models import init_db, SessionLocal, Job, Skill
from scraper.job_collector import job_collector
from analytics.data_pipeline import data_pipeline
from nlp.skill_extractor import skill_extractor, SKILL_TAXONOMY
from nlp.recommender import skill_recommender

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database schema and initial seed data upon startup
with app.app_context():
    init_db()
    seed_result = job_collector.seed_initial_data()
    data_pipeline.load_and_clean_data()
    print("Database and analytics pipeline initialized.")

@app.context_processor
def inject_global_data():
    """Provides common data across all Jinja2 templates."""
    return {
        'target_roles': Config.TARGET_ROLES,
        'all_skills': sorted(list(SKILL_TAXONOMY.keys()))
    }

# ======================== PAGE ROUTES ========================

@app.route('/')
def dashboard():
    """Main Executive Analytics Dashboard."""
    overview = data_pipeline.get_market_overview()
    top_skills = data_pipeline.get_top_demanded_skills(limit=10)
    salary_leaders = data_pipeline.get_skill_salary_analysis(min_mentions=2)[:8]
    work_modes = data_pipeline.get_work_mode_stats()
    role_dist = data_pipeline.get_role_distribution()
    experience_trends = data_pipeline.get_experience_salary_trends()

    return render_template(
        'index.html',
        overview=overview,
        top_skills=top_skills,
        salary_leaders=salary_leaders,
        work_modes=work_modes,
        role_dist=role_dist,
        experience_trends=experience_trends
    )

@app.route('/jobs')
def jobs():
    """Job Listings Explorer with Search, Filtering & Pagination."""
    search_query = request.args.get('q', '').strip()
    role_filter = request.args.get('role', 'All')
    mode_filter = request.args.get('mode', 'All')
    skill_filter = request.args.get('skill', 'All')
    page = int(request.args.get('page', 1))
    per_page = 12

    session = SessionLocal()
    try:
        query = session.query(Job)

        if search_query:
            term = f"%{search_query}%"
            query = query.filter(
                (Job.title.ilike(term)) |
                (Job.company.ilike(term)) |
                (Job.description.ilike(term))
            )

        if role_filter != 'All':
            query = query.filter(Job.role_category == role_filter)

        if mode_filter != 'All':
            query = query.filter(Job.work_mode == mode_filter)

        if skill_filter != 'All':
            query = query.filter(Job.skills.any(Skill.name == skill_filter))

        total_count = query.count()
        jobs_list = query.order_by(Job.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        # Convert to dictionaries for template rendering
        job_dicts = [j.to_dict() for j in jobs_list]
        total_pages = max(1, (total_count + per_page - 1) // per_page)

        return render_template(
            'jobs.html',
            jobs=job_dicts,
            total_jobs=total_count,
            page=page,
            total_pages=total_pages,
            search_query=search_query,
            role_filter=role_filter,
            mode_filter=mode_filter,
            skill_filter=skill_filter
        )
    finally:
        session.close()

@app.route('/skills')
def skills():
    """In-depth Skill Matrix & Salary Premium Benchmark."""
    salary_analysis = data_pipeline.get_skill_salary_analysis(min_mentions=1)
    top_skills = data_pipeline.get_top_demanded_skills(limit=30)
    
    # Calculate categories counts
    all_skills_info = skill_extractor.get_all_skills()

    return render_template(
        'skills.html',
        salary_analysis=salary_analysis,
        top_skills=top_skills,
        skills_catalog=all_skills_info
    )

@app.route('/recommender', methods=['GET', 'POST'])
def recommender():
    """Interactive Skill Gap Analyzer & Career Roadmap Generator."""
    analysis_result = None
    initial_skills = ""
    initial_role = "Backend Developer"
    initial_resume = ""
    initial_jd = ""

    if request.method == 'POST':
        initial_skills = request.form.get('user_skills', '')
        initial_role = request.form.get('target_role', 'Backend Developer')
        initial_resume = request.form.get('resume_text', '')
        initial_jd = request.form.get('custom_jd', '')

        analysis_result = skill_recommender.analyze_gap(
            user_skills_input=initial_skills,
            resume_text=initial_resume,
            target_role=initial_role,
            custom_job_description=initial_jd
        )

    return render_template(
        'recommender.html',
        result=analysis_result,
        initial_skills=initial_skills,
        initial_role=initial_role,
        initial_resume=initial_resume,
        initial_jd=initial_jd
    )

@app.route('/scraper')
def scraper_control():
    """Data Pipeline & Live Scraper Control Center."""
    session = SessionLocal()
    try:
        total_jobs = session.query(Job).count()
        total_skills = session.query(Skill).count()
        recent_jobs = session.query(Job).order_by(Job.id.desc()).limit(5).all()
        recent_jobs_dict = [j.to_dict() for j in recent_jobs]
    finally:
        session.close()

    return render_template(
        'scraper.html',
        total_jobs=total_jobs,
        total_skills=total_skills,
        recent_jobs=recent_jobs_dict
    )

# ======================== API ENDPOINTS ========================

@app.route('/api/stats')
def api_stats():
    """Returns aggregated charts data for Chart.js rendering."""
    role_filter = request.args.get('role', 'All')
    
    top_skills = data_pipeline.get_top_demanded_skills(limit=12, role_filter=role_filter)
    salary_analysis = data_pipeline.get_skill_salary_analysis(min_mentions=2)[:10]
    work_modes = data_pipeline.get_work_mode_stats()
    experience_trends = data_pipeline.get_experience_salary_trends()
    role_dist = data_pipeline.get_role_distribution()

    return jsonify({
        'top_skills': top_skills,
        'salary_analysis': salary_analysis,
        'work_modes': work_modes,
        'experience_trends': experience_trends,
        'role_distribution': role_dist
    })

@app.route('/api/skill-cooccurrence/<skill_name>')
def api_skill_cooccurrence(skill_name):
    """Returns co-occurrence correlations for a given skill."""
    data = data_pipeline.get_skill_cooccurrence(skill_name, top_n=6)
    return jsonify(data)

@app.route('/api/analyze-gap', methods=['POST'])
def api_analyze_gap():
    """API endpoint for asynchronous skill gap analysis."""
    payload = request.get_json() or {}
    user_skills = payload.get('skills', '')
    resume = payload.get('resume', '')
    role = payload.get('role', 'Backend Developer')
    custom_jd = payload.get('custom_jd', '')

    result = skill_recommender.analyze_gap(
        user_skills_input=user_skills,
        resume_text=resume,
        target_role=role,
        custom_job_description=custom_jd
    )
    return jsonify(result)

@app.route('/api/scrape/trigger', methods=['POST'])
def api_trigger_scrape():
    """Triggers live ingestion from permitted sources or synthetic stream."""
    source_type = request.form.get('source_type', 'stream')
    count = int(request.form.get('count', 15))

    collected = []
    if source_type == 'remoteok':
        collected = job_collector.fetch_from_remoteok(limit=count)
    elif source_type == 'arbeitnow':
        collected = job_collector.fetch_from_arbeitnow(limit=count)
    else:
        # Live streaming simulation batch
        collected = job_collector.generate_synthetic_stream(count=count)

    ingest_result = job_collector.ingest_to_db(collected)
    data_pipeline.load_and_clean_data()

    flash(f"Successfully processed {len(collected)} job postings! Added {ingest_result['new_jobs']} new unique jobs and {ingest_result['new_skills']} new skills.", "success")
    return redirect(url_for('scraper_control'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    print(f"Job Market Intelligence Platform running at http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
