from fastapi.testclient import TestClient
from lingominer.api.auth.schemas import UserDetail


def test_get_me(client: TestClient, example_user: UserDetail):
    response = client.get("/me")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == example_user.id
    assert data["name"] == example_user.name


def test_update_settings(client: TestClient):
    settings_data = {"mochi_api_key": "test_api_key"}
    response = client.patch("/me/settings", json=settings_data)
    assert response.status_code == 200
    data = response.json()
    assert data["mochi_api_key"] == settings_data["mochi_api_key"]
