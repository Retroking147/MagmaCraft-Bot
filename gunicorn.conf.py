import os

bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = 1
worker_class = "sync"
timeout = 120
keepalive = 30
max_requests = 1000
max_requests_jitter = 100
preload_app = True