import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fastapi-app"))
from coach import analyze_bowling_game, coach_response


PERFECT_GAME = [["X"] for _ in range(9)] + [["X", "X", "X"]]
EXAMPLE_GAME = [
    ["8", "/"], ["5", "4"], ["9", "0"], ["X"], ["X"],
    ["5", "/"], ["5", "3"], ["6", "3"], ["9", "/"], ["9", "/", "X"],
]


def test_perfect_game_analysis_counts_all_twelve_strikes():
    result = analyze_bowling_game(PERFECT_GAME)

    assert result["valid"] is True
    assert result["strikes"] == 12
    assert result["spares"] == 0
    assert result["open_frames"] == 0


def test_perfect_300_gets_congratulations_not_spare_advice(monkeypatch):
    monkeypatch.delenv("AI_GATEWAY_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    answer = coach_response("How did I do?", PERFECT_GAME, 300)

    assert "perfect 300 game" in answer.lower()
    assert "congratulations" in answer.lower()
    assert "spare conversion" not in answer.lower()
    assert "spare chances" not in answer.lower()


def test_invalid_tenth_frame_strike_slash_is_rejected():
    frames = [["9", "0"] for _ in range(9)] + [["X", "/", "X"]]

    result = analyze_bowling_game(frames)

    assert result["valid"] is False
    assert "cannot immediately follow a strike" in result["error"]


def test_open_frames_report_spare_shooting_opportunity(monkeypatch):
    monkeypatch.delenv("AI_GATEWAY_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    frames = [["9", "0"] for _ in range(9)] + [["9", "0"]]

    result = analyze_bowling_game(frames)
    answer = coach_response("What should I practice?", frames, 90)

    assert result["open_frames"] == 10
    assert "10 open frames" in answer
    assert "spare shooting" in answer.lower()


def test_fallback_uses_correct_singular_grammar(monkeypatch):
    monkeypatch.delenv("AI_GATEWAY_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    frames = [["X"] for _ in range(9)] + [["X", "X", "X"]]

    answer = coach_response("How did I do?", frames, 300)

    assert "1 strike" not in answer  # perfect-game response is special-cased
