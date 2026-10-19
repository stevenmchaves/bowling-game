import importlib.util
import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
for path in (ROOT / "src", ROOT, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Load the repository's root main.py by file path under a unique module name.
# This avoids importing this FastAPI file recursively as module `main`.
ROOT_MAIN = ROOT / "main.py"
spec = importlib.util.spec_from_file_location("bowling_game_cli_main", ROOT_MAIN)
if spec is None or spec.loader is None:
    raise ImportError(f"Unable to load bowling game pipeline from {ROOT_MAIN}")
root_main = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = root_main
spec.loader.exec_module(root_main)
game_pipeline = root_main.game_pipeline

from coach import coach_response

app = FastAPI(title="Bowling Game FastAPI")
STATIC_DIR = APP_DIR / "static"


class PlayerScoreRequest(BaseModel):
    name: str | None = None
    frames: list[list[str]]


class ScoreRequest(BaseModel):
    frames: list[list[str]] | None = None
    players: list[PlayerScoreRequest] | None = None


class CoachRequest(BaseModel):
    question: str
    frames: list[list[str]]
    score: int


def _score_frames(frames: list[list[str]]) -> dict:
    game = game_pipeline(json.dumps(frames))
    board = game.get_scoreboard_data()
    return {
        "score": game.score(),
        "cumulative_scores": board["cumulative_scores"],
        "display_frames": board["display_frames"],
        "frames": game.raw_frames,
    }


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
        if payload.players is not None:
            if not payload.players:
                raise HTTPException(status_code=400, detail="Request body must include a non-empty 'players' list.")
            results = []
            for index, player in enumerate(payload.players, start=1):
                name = (player.name or "").strip() or f"Player {index}"
                try:
                    results.append({"name": name, **_score_frames(player.frames)})
                except Exception as exc:
                    raise HTTPException(status_code=400, detail=f"Player '{name}': {exc}") from exc
            return {"players": results}

        if payload.frames is None:
            raise HTTPException(status_code=400, detail="Request body must include a 'frames' list or a 'players' list.")
        return _score_frames(payload.frames)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/coach")
def coach(payload: CoachRequest) -> dict[str, str]:
    try:
        return {"answer": coach_response(payload.question, payload.frames, payload.score)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="The bowling coach is temporarily unavailable.") from exc
