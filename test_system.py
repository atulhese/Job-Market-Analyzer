import os
import sys

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_tests():
    import app
    client = app.app.test_client()

    print("\n--- TEST 1: Executive Dashboard Route ---")
    r_dash = client.get('/')
    assert r_dash.status_code == 200, f"Dashboard failed: {r_dash.status_code}"
    print("✓ Dashboard status 200 OK")

    print("\n--- TEST 2: Market Stats API ---")
    r_stats = client.get('/api/stats')
    assert r_stats.status_code == 200
    stats = r_stats.get_json()
    print(f"✓ Extracted Top Skills count: {len(stats['top_skills'])}")
    for s in stats['top_skills'][:5]:
        print(f"  - {s['skill']}: {s['count']} postings ({s['percentage']}%)")

    print("\n--- TEST 3: Skill Co-occurrence API ---")
    r_co = client.get('/api/skill-cooccurrence/Python')
    assert r_co.status_code == 200
    co_data = r_co.get_json()
    print("✓ Python pairings found:")
    for c in co_data[:4]:
        print(f"  - {c['skill']}: {c['co_percentage']}% of Python jobs")

    print("\n--- TEST 4: Job Listings Explorer ---")
    r_jobs = client.get('/jobs?role=Backend+Developer')
    assert r_jobs.status_code == 200
    print("✓ Jobs explorer status 200 OK")

    print("\n--- TEST 5: Skills Matrix Route ---")
    r_skills = client.get('/skills')
    assert r_skills.status_code == 200
    print("✓ Skills matrix benchmark status 200 OK")

    print("\n--- TEST 6: Skill Gap & Career Roadmap Recommender ---")
    r_gap = client.post('/api/analyze-gap', json={
        'skills': 'Python, Flask, SQLite',
        'role': 'Backend Developer'
    })
    assert r_gap.status_code == 200
    gap = r_gap.get_json()
    print(f"✓ Target Role: {gap['target_title']}")
    print(f"✓ Candidate Match Score: {gap['match_score']}%")
    print(f"✓ High-ROI Missing Skills: {[m['skill'] for m in gap['missing_skills'][:4]]}")
    print(f"✓ Estimated Salary Uplift: +${gap['estimated_salary_boost']:,} / year")
    print(f"✓ 4-Week Roadmap Generated ({len(gap['roadmap'])} milestones)")
    for step in gap['roadmap']:
        print(f"  [{step['week']}] {step['phase']}")

    print("\n--- TEST 7: Scraper Pipeline Ingestion Trigger ---")
    r_scrape = client.post('/api/scrape/trigger', data={
        'source_type': 'stream',
        'count': 10
    }, follow_redirects=True)
    assert r_scrape.status_code == 200
    print("✓ Live Ingestion Pipeline Trigger: 200 OK")

    print("\n=======================================================")
    print("🎉 ALL 7 SYSTEM TESTS PASSED SUCCESSFULLY!")
    print("=======================================================\n")

if __name__ == '__main__':
    run_tests()
