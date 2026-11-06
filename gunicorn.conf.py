import os

# Render dynamically assigns a PORT environment variable (e.g., 10000)
# It is critical to bind to 0.0.0.0 and the assigned PORT
port = os.environ.get("PORT", "5050")
bind = f"0.0.0.0:{port}"

workers = 2
threads = 4
timeout = 120
accesslog = "-"
errorlog = "-"
