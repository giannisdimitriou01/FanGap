from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_games_includes_hades() -> None:
    response = client.get("/games", params={"q": "Hades"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert any(item["title"] == "Hades" for item in payload["items"])
    assert "genres" in payload
    assert "platforms" in payload


def test_get_game_not_found() -> None:
    response = client.get("/games/999999")
    assert response.status_code == 404


def test_game_detail_and_history() -> None:
    listed = client.get("/games", params={"q": "Hades"}).json()["items"]
    game_id = listed[0]["id"]
    detail = client.get(f"/games/{game_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["title"] == "Hades"
    history = client.get(f"/games/{game_id}/ratings/history")
    assert history.status_code == 200
    assert len(history.json()["items"]) >= 1
    latest = client.get(f"/games/{game_id}/ratings")
    assert latest.status_code == 200


def test_divergence_leaderboard() -> None:
    response = client.get("/games/divergence/top")
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    gaps = [float(row["divergence"]) for row in items]
    assert gaps == sorted(gaps, reverse=True)


def test_sort_by_divergence() -> None:
    response = client.get("/games", params={"sort": "divergence"})
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    ranked = [item for item in items if item["divergence"] is not None]
    gaps = [item["divergence"] for item in ranked]
    assert gaps == sorted(gaps, reverse=True)
