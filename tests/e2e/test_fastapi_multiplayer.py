from fastapi.testclient import TestClient

from fastapi_app import app


client = TestClient(app)
PERFECT_GAME = [["X"] for _ in range(9)] + [["X", "X", "X"]]
EXAMPLE_GAME = [
    ["8", "/"], ["5", "4"], ["9", "0"], ["X"], ["X"],
    ["5", "/"], ["5", "3"], ["6", "3"], ["9", "/"], ["9", "/", "X"],
]


def test_react_frontend_contains_add_player_control():
    from pathlib import Path

    app_source = (Path(__file__).resolve().parents[1] / "react-frontend" / "src" / "App.jsx").read_text(encoding="utf-8")
    assert "+ Add Player" in app_source
    assert "const addPlayer" in app_source
    assert "Remove" in app_source


def test_fastapi_multiplayer_score_endpoint_returns_each_player():
    response = client.post("/api/score", json={"players": [
        {"name": "Alice", "frames": EXAMPLE_GAME},
        {"name": "Bob", "frames": PERFECT_GAME},
    ]})

    assert response.status_code == 200
    body = response.json()
    assert [player["name"] for player in body["players"]] == ["Alice", "Bob"]
    assert body["players"][0]["score"] == 149
    assert body["players"][1]["score"] == 300


def test_fastapi_multiplayer_endpoint_rejects_empty_players():
    response = client.post("/api/score", json={"players": []})

    assert response.status_code == 400
    assert "non-empty 'players' list" in response.json()["detail"]


def test_fastapi_single_player_score_endpoint_remains_compatible():
    response = client.post("/api/score", json={"frames": PERFECT_GAME})

    assert response.status_code == 200
    assert response.json()["score"] == 300


def test_fastapi_index_page_is_served():
    response = client.get("/")

    assert response.status_code == 200
    assert "Add Player" in response.text
