from fastapi.testclient import TestClient
from lingominer.models.template import TemplateLang


def test_template_crud(client: TestClient):
    # Test template creation
    template_data = {
        "name": "Test Template",
        "lang": TemplateLang.EN,
    }
    response = client.post("/templates", json=template_data)
    assert response.status_code == 200
    created = response.json()
    assert created["name"] == template_data["name"]
    assert created["lang"] == template_data["lang"]
    assert "id" in created

    # Test getting single template
    response = client.get(f"/templates/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["name"] == created["name"]

    # Test getting all templates
    template2_data = {
        "name": "Test Template 2",
        "lang": TemplateLang.EN,
    }
    response = client.post("/templates", json=template2_data)
    template2 = response.json()

    response = client.get("/templates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    template_ids = [t["id"] for t in data]
    assert created["id"] in template_ids
    assert template2["id"] in template_ids

    # Test template deletion
    response = client.delete(f"/templates/{created['id']}")
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f"/templates/{created['id']}")
    assert response.status_code == 404
