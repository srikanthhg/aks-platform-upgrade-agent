"""Container entry point for the background workflow worker.

The worker implementation remains in backend/worker.py so it continues to
reuse the backend's existing queue, workflow services, configuration and
logging without maintaining a second copy of that logic.
"""
from pathlib import Path
import runpy

BACKEND_WORKER = Path(__file__).resolve().parents[1] / "worker.py"

if not BACKEND_WORKER.is_file():
    raise FileNotFoundError(f"Backend worker implementation not found: {BACKEND_WORKER}")

runpy.run_path(str(BACKEND_WORKER), run_name="__main__")
