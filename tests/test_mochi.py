from fastapi.testclient import TestClient

from lingominer.models.user import User


def test_get_mochi_templates(client: TestClient, example_user: User):
    # First set the mochi api key
    settings_data = {
        "mochi_api_key": "test_api_key"
    }
    client.patch("/me/settings", json=settings_data)

    response = client.get("/mochi")
    assert response.status_code == 200
    data = response.json()
    assert "docs" in data
    assert isinstance(data["docs"], list)


def test_get_mochi_template(client: TestClient, example_user: User):
    # First set the mochi api key
    settings_data = {
        "mochi_api_key": "test_api_key"
    }
    client.patch("/me/settings", json=settings_data)

    # Get a template id from the list
    response = client.get("/mochi")
    template_id = response.json()["docs"][0]["id"]

    response = client.get(f"/mochi/{template_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == template_id
    assert "content" in data
    assert "fields" in data


def test_create_mochi_mapping(client: TestClient, example_user: User, test_template):
    # First set the mochi api key
    settings_data = {
        "mochi_api_key": "test_api_key"
    }
    client.patch("/me/settings", json=settings_data)

    # Get a template id from the list
    response = client.get("/mochi")
    mochi_template_id = response.json()["docs"][0]["id"]

    mapping_data = {
        "lingominer_template_id": test_template.id,
        "lingominer_template_name": test_template.name,
        "mapping": {
            "field1": {"name": "field1", "id": "field1_id"},
            "field2": {"name": "field2", "id": "field2_id"}
        }
    }

    response = client.post(f"/mochi/{mochi_template_id}/mapping", json=mapping_data)
    assert response.status_code == 200
    data = response.json()
    assert data["mochi_template_id"] == mochi_template_id
    assert data["lingominer_template_id"] == test_template.id
    assert data["mapping"] == mapping_data["mapping"]


def test_delete_mochi_mapping(client: TestClient, example_user: User, test_template):
    # First set the mochi api key
    settings_data = {
        "mochi_api_key": "test_api_key"
    }
    client.patch("/me/settings", json=settings_data)

    # Get a template id from the list
    response = client.get("/mochi")
    mochi_template_id = response.json()["docs"][0]["id"]

    # Create a mapping first
    mapping_data = {
        "lingominer_template_id": test_template.id,
        "lingominer_template_name": test_template.name,
        "mapping": {
            "field1": {"name": "field1", "id": "field1_id"},
            "field2": {"name": "field2", "id": "field2_id"}
        }
    }
    client.post(f"/mochi/{mochi_template_id}/mapping", json=mapping_data)

    # Test deletion
    response = client.delete(f"/mochi/{mochi_template_id}/mapping")
    assert response.status_code == 200 