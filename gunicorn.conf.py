import os

# Render dynamically assigns a PORT environment variable (e.g., 10000)
# It is critical to bind to 0.0.0.0 and the assigned PORT
port = os.environ.get("PORT", "5050")
bind = f"0.0.0.0:{port}"

# 1 worker + 4 threads: optimal for Render free tier (512MB RAM limit)
# Prevents SQLite multi-process file locking while maintaining concurrent request handling
workers = 1
threads = 4
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"
