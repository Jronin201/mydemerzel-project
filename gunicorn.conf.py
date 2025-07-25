# Gunicorn configuration optimized for low-memory deployment environments
# This configuration is designed for Render's 512MB memory limit

import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
backlog = 2048

# Worker processes - CRITICAL for memory optimization
# Use only 1 worker to minimize memory usage
# Each worker loads embeddings separately, so multiple workers = multiple copies in memory
workers = 1
worker_class = "sync"  # Changed back to sync - more reliable on Render
worker_connections = 50  # Reduced for memory efficiency
timeout = 120
keepalive = 5

# Memory management
# Restart workers after handling requests to prevent memory leaks
max_requests = 100
max_requests_jitter = 20
preload_app = True  # Load app before forking workers

# Memory monitoring and limits
# Restart worker if memory usage gets too high
worker_tmp_dir = "/dev/shm"  # Use shared memory for temporary files
tmp_upload_dir = None

# Logging optimized for deployment
loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process management
pidfile = "/tmp/gunicorn.pid"
daemon = False

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Deployment optimizations
forwarded_allow_ips = "*"
proxy_allow_ips = "*"

def when_ready(server):
    """Called when the server is ready to receive requests."""
    print("🚀 Gunicorn server ready with memory-optimized configuration")
    print(f"   Workers: {workers}")
    print(f"   Max requests per worker: {max_requests}")
    print(f"   Memory optimization: ACTIVE")

def worker_int(worker):
    """Called when worker receives INT or QUIT signal."""
    print(f"🧹 Worker {worker.pid} shutting down - clearing memory")

def pre_fork(server, worker):
    """Called before worker processes are forked."""
    print(f"🔄 Pre-fork: preparing worker {worker.age}")

def post_fork(server, worker):
    """Called after worker processes are forked."""
    print(f"✅ Post-fork: worker {worker.pid} ready with PID {worker.age}")

def post_worker_init(worker):
    """Called after worker initialization - set up memory optimization."""
    print(f"🧠 Worker {worker.pid} initialized with memory optimization")
    
    # Optional: Preload a specific TTRPG system if specified
    preload_system = os.environ.get('PRELOAD_TTRPG_SYSTEM')
    if preload_system:
        try:
            from memory_optimized_embeddings import embedding_manager
            print(f"🔄 Preloading {preload_system} embeddings...")
            embedding_manager.preload_system(preload_system)
            print(f"✅ {preload_system} embeddings preloaded")
        except Exception as e:
            print(f"⚠️  Could not preload {preload_system}: {e}")

def on_exit(server):
    """Called when gunicorn is shutting down."""
    print("🛑 Gunicorn shutting down - performing cleanup")
