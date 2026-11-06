// Skill Gap Analyzer and Interactive Recommender Presets

document.addEventListener('DOMContentLoaded', () => {
    // Preset profile loader
    window.loadProfilePreset = function(presetType) {
        const skillsInput = document.getElementById('user_skills');
        const roleSelect = document.getElementById('target_role');
        const resumeText = document.getElementById('resume_text');

        if (!skillsInput || !roleSelect) return;

        if (presetType === 'python-backend') {
            skillsInput.value = "Python, Flask, SQLite, Git, HTML, CSS";
            roleSelect.value = "Backend Developer";
            if (resumeText) resumeText.value = "Junior developer with 1.5 years experience building Flask APIs and relational databases. Seeking to transition into high-scale Django and microservices.";
        } else if (presetType === 'mern-fullstack') {
            skillsInput.value = "JavaScript, React, Node.js, Express, MongoDB, Git";
            roleSelect.value = "Full Stack Developer";
            if (resumeText) resumeText.value = "Frontend focused developer proficient in React and Node.js looking to expand into TypeScript, SQL/PostgreSQL, and cloud deployments on AWS.";
        } else if (presetType === 'aspiring-ml') {
            skillsInput.value = "Python, Pandas, NumPy, Scikit-learn, SQL";
            roleSelect.value = "Machine Learning Engineer";
            if (resumeText) resumeText.value = "Data Analyst with strong Python and classical ML knowledge. Aiming to upskill in PyTorch, LLMs, LangChain, and RAG architectures.";
        } else if (presetType === 'devops-junior') {
            skillsInput.value = "Linux, Git, Python, Bash, Docker";
            roleSelect.value = "DevOps Engineer";
            if (resumeText) resumeText.value = "Systems administrator skilled in Linux and Docker containers. Looking to master Kubernetes, Terraform, and CI/CD pipelines on AWS.";
        }
    };
});
