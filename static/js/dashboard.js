// Interactive Dashboard Analytics Engine using Chart.js

let topSkillsChartInstance = null;
let salaryChartInstance = null;
let workModeChartInstance = null;
let experienceChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    initDashboardCharts();

    const roleSelector = document.getElementById('dashboard-role-filter');
    if (roleSelector) {
        roleSelector.addEventListener('change', (e) => {
            updateDashboardCharts(e.target.value);
        });
    }
});

async function initDashboardCharts() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        renderAllCharts(data);
    } catch (err) {
        console.error('Error fetching dashboard statistics:', err);
    }
}

async function updateDashboardCharts(role) {
    try {
        const response = await fetch(`/api/stats?role=${encodeURIComponent(role)}`);
        const data = await response.json();
        
        // Update top skills chart
        if (topSkillsChartInstance) {
            topSkillsChartInstance.data.labels = data.top_skills.map(s => s.skill);
            topSkillsChartInstance.data.datasets[0].data = data.top_skills.map(s => s.count);
            topSkillsChartInstance.update();
        }
    } catch (err) {
        console.error('Error updating charts for role:', err);
    }
}

function renderAllCharts(data) {
    Chart.defaults.color = '#9ca3af';
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

    // 1. Top In-Demand Skills Chart (Horizontal Bar)
    const ctxSkills = document.getElementById('topSkillsChart');
    if (ctxSkills) {
        const labels = data.top_skills.map(s => s.skill);
        const counts = data.top_skills.map(s => s.count);

        topSkillsChartInstance = new Chart(ctxSkills, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Job Postings Mentioning Skill',
                    data: counts,
                    backgroundColor: 'rgba(99, 102, 241, 0.75)',
                    borderColor: '#6366f1',
                    borderWidth: 1,
                    borderRadius: 6,
                    hoverBackgroundColor: '#818cf8'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.raw} postings (${data.top_skills[ctx.dataIndex]?.percentage || 0}%)`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: { stepSize: 2 }
                    },
                    y: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // 2. Highest Paying Skills vs Market Average (Vertical Bar)
    const ctxSalary = document.getElementById('salaryComparisonChart');
    if (ctxSalary) {
        const sLabels = data.salary_analysis.map(s => s.skill);
        const sValues = data.salary_analysis.map(s => s.avg_salary);

        salaryChartInstance = new Chart(ctxSalary, {
            type: 'bar',
            data: {
                labels: sLabels,
                datasets: [{
                    label: 'Average Annual Salary (USD)',
                    data: sValues,
                    backgroundColor: 'rgba(16, 185, 129, 0.75)',
                    borderColor: '#10b981',
                    borderWidth: 1,
                    borderRadius: 6,
                    hoverBackgroundColor: '#34d399'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` $${ctx.raw.toLocaleString()} / year`
                        }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            callback: (v) => `$${v / 1000}k`
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // 3. Work Mode Distribution (Doughnut)
    const ctxWorkMode = document.getElementById('workModeChart');
    if (ctxWorkMode) {
        const wLabels = data.work_modes.map(w => `${w.mode} (${w.percentage}%)`);
        const wCounts = data.work_modes.map(w => w.count);

        workModeChartInstance = new Chart(ctxWorkMode, {
            type: 'doughnut',
            data: {
                labels: wLabels,
                datasets: [{
                    data: wCounts,
                    backgroundColor: [
                        'rgba(6, 182, 212, 0.8)',
                        'rgba(99, 102, 241, 0.8)',
                        'rgba(245, 158, 11, 0.8)'
                    ],
                    borderColor: '#111827',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 15 }
                    }
                },
                cutout: '68%'
            }
        });
    }

    // 4. Experience Level vs Salary Curve (Bar)
    const ctxExp = document.getElementById('experienceSalaryChart');
    if (ctxExp) {
        const eLabels = data.experience_trends.map(e => e.level);
        const eSalaries = data.experience_trends.map(e => e.avg_salary);

        experienceChartInstance = new Chart(ctxExp, {
            type: 'bar',
            data: {
                labels: eLabels,
                datasets: [{
                    label: 'Mean Salary (USD)',
                    data: eSalaries,
                    backgroundColor: 'rgba(245, 158, 11, 0.75)',
                    borderColor: '#f59e0b',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` $${ctx.raw.toLocaleString()} avg`
                        }
                    }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        ticks: {
                            callback: (v) => `$${v / 1000}k`
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
}
