"""
Gunicorn configuration for production deployment.
Uses Uvicorn workers for ASGI support.
"""

import multiprocessing
import os

# Bind to Unix socket or TCP
bind = os.getenv("GUNICORN_BIND", "unix:/run/cds-api/gunicorn.sock")
# Alternative: bind = "0.0.0.0:8000"

# Worker configuration
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5

# Process naming
proc_name = "cds-api"

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = os.getenv("LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
daemon = False
pidfile = "/run/cds-api/gunicorn.pid"
user = os.getenv("GUNICORN_USER", "cds-api")
group = os.getenv("GUNICORN_GROUP", "cds-api")
tmp_upload_dir = None

# SSL (handled by Nginx in production)
# keyfile = None
# certfile = None

# Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    pass

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    pass

def worker_abort(worker):
    """Called when a worker times out."""
    pass
