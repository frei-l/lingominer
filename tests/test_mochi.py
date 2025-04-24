from fastapi.testclient import TestClient


monk_template = {
    "id": "monk_template",
    "name": "Monk Template",
    "content": "Monk Template Content",
    "fields": {
        "field1": {"name": "field1", "id": "field1_id"},
        "field2": {"name": "field2", "id": "field2_id"},
    },
}


def test_get_mochi_deck_mappings(client: TestClient):
    response = client.get("/mochi")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If there are any decks
        assert "id" in data[0]
        assert "name" in data[0]
        assert "template_id" in data[0]


def test_get_mochi_deck_mapping(client: TestClient):
    # First get a deck id
    response = client.get("/mochi")
    deck_id = response.json()[0]["id"]

    response = client.get(f"/mochi/{deck_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == deck_id
    assert "template_name" in data
    assert "template_content" in data
    assert "template_fields" in data


def test_create_mochi_mapping(client: TestClient):
    # Get a deck id and template id from the list
    response = client.get("/mochi")
    deck_data = response.json()[0]
    mochi_deck_id = deck_data["id"]
    mochi_template_id = deck_data["template_id"]

    mapping_data = {
        "mochi_deck_id": mochi_deck_id,
        "mochi_template_id": mochi_template_id,
        "lingominer_template_id": monk_template["id"],
        "lingominer_template_name": monk_template["name"],
        "mapping": {
            "field1": {"name": "field1", "id": "field1_id"},
            "field2": {"name": "field2", "id": "field2_id"},
        },
    }

    response = client.post("/mochi", json=mapping_data)
    assert response.status_code == 200
    data = response.json()
    assert data["mochi_deck_id"] == mochi_deck_id
    assert data["mochi_template_id"] == mochi_template_id
    assert data["lingominer_template_id"] == monk_template["id"]
    assert data["mapping"] == mapping_data["mapping"]


def test_delete_mochi_mapping(client: TestClient):
    # Get a deck id from the list
    response = client.get("/mochi")
    mochi_deck_id = response.json()[0]["id"]

    # Create a mapping first
    deck_data = response.json()[0]
    mapping_data = {
        "mochi_deck_id": mochi_deck_id,
        "mochi_template_id": deck_data["template_id"],
        "lingominer_template_id": monk_template["id"],
        "lingominer_template_name": monk_template["name"],
        "mapping": {
            "field1": {"name": "field1", "id": "field1_id"},
            "field2": {"name": "field2", "id": "field2_id"},
        },
    }
    client.post("/mochi", json=mapping_data)

    # Test deletion
    response = client.delete(f"/mochi/{mochi_deck_id}")
    assert response.status_code == 200
