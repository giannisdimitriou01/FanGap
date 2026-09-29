from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_featured_list_includes_hades() -> None:
    response = client.get("/games")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert any(item["title"] == "Hades" for item in payload["items"])
    assert payload["items"][0]["featured_rank"] is not None


def test_get_game_not_found() -> None:
    response = client.get("/games/999999")
    assert response.status_code == 404


def test_featured_detail_and_history() -> None:
    listed = client.get("/games").json()["items"]
    game_id = listed[0]["id"]
    detail = client.get(f"/games/{game_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["title"] == "Hades"
    history = client.get(f"/games/{game_id}/ratings/history")
    assert history.status_code == 200
    assert len(history.json()["items"]) >= 1


def test_featured_divergence_leaderboard() -> None:
    response = client.get("/games/divergence/top")
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    gaps = [float(row["divergence"]) for row in items if row["divergence"] is not None]
    assert gaps == sorted(gaps, reverse=True)


def test_live_leaderboard_empty_until_built() -> None:
    response = client.get("/leaderboard/live")
    assert response.status_code == 200
    payload = response.json()
    assert "items" in payload
