"""Vercel-compatible importable entrypoint for the FastAPI application."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_DIR = ROOT / "fastapi-app"
APP_MAIN = APP_DIR / "main.py"

# The app's sibling coach module lives in a directory with a hyphen, so add
# that directory to the import path before loading its main module.
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

spec = importlib.util.spec_from_file_location("bowling_fastapi_app", APP_MAIN)
if spec is None or spec.loader is None:
    raise ImportError(f"Unable to load FastAPI application from {APP_MAIN}")

module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

app = module.app
