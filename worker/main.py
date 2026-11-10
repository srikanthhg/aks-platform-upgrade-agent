"""Container entry point for the background workflow worker.

The worker implementation remains in the backend source and is copied to
/app/worker.py by backend/Dockerfile. This entry point reuses that code rather
than maintaining a second copy of the queue and workflow logic.
"""
from pathlib import Path
import runpy
import sys

APP_DIR = Path(__file__).resolve().parents[1]
BACKEND_WORKER = APP_DIR / "worker.py"

if not BACKEND_WORKER.is_file():
    raise FileNotFoundError(f"Backend worker implementation not found: {BACKEND_WORKER}")

# The backend image stores config.py, services/, graph/ and tools/ directly
# under /app. Add that directory so the existing top-level imports resolve.
sys.path.insert(0, str(APP_DIR))
runpy.run_path(str(BACKEND_WORKER), run_name="__main__")
