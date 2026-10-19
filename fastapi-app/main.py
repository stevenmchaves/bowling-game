import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import game_pipeline

app = FastAPI(title="Bowling Game FastAPI")
STATIC_DIR = Path(__file__).resolve().parent / "static"


class ScoreRequest(BaseModel):
    frames: list[list[str]]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/index.html")
def index_html() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/score")
def score_game(payload: ScoreRequest) -> dict:
    try:
        game = game_pipeline(json.dumps(payload.frames))
        board = game.get_scoreboard_data()
        return {
            "score": game.score(),
            "cumulative_scores": board["cumulative_scores"],
            "display_frames": board["display_frames"],
            "frames": game.raw_frames,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive API path
        raise HTTPException(status_code=400, detail=str(exc)) from exc
