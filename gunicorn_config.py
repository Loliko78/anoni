import os

bind = f"0.0.0.0:{os.environ.get('PORT', 8080)}"
workers = 1
worker_class = "eventlet"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True