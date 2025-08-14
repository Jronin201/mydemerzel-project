import os, time, threading, socket
import pytest

# Ensure test mode
os.environ.setdefault('TESTING','1')

_server_started = False
_server_lock = threading.Lock()

def _is_port_open(host='127.0.0.1', port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        try:
            s.connect((host, port))
            return True
        except Exception:
            return False

def _start_flask_app():
    from app import app  # import here after env
    from werkzeug.serving import make_server
    server = make_server('127.0.0.1', 5000, app)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    # wait until responsive
    for _ in range(50):
        if _is_port_open():
            break
        time.sleep(0.1)

@pytest.fixture(scope='session', autouse=True)
def ensure_server():
    global _server_started
    with _server_lock:
        if not _server_started and not _is_port_open():
            _start_flask_app()
            _server_started = True
    yield
