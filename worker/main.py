"""Container entry point for the background workflow worker.

The worker implementation remains in backend/worker.py so it continues to
reuse the backend's existing queue, workflow services, configuration and
logging without maintaining a second copy of that logic.
"""
from pathlib import Path
import runpy
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPOSITORY_ROOT / "backend"
BACKEND_WORKER = BACKEND_DIR / "worker.py"

if not BACKEND_WORKER.is_file():
    raise FileNotFoundError(f"Backend worker implementation not found: {BACKEND_WORKER}")

# backend/worker.py imports modules such as config and services as top-level
# modules, so its directory must be on sys.path when executed from this package.
sys.path.insert(0, str(BACKEND_DIR))
runpy.run_path(str(BACKEND_WORKER), run_name="__main__")
