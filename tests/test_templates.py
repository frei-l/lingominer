from fastapi.testclient import TestClient

from lingominer.models.template import TemplateLang


def test_template_crud(client: TestClient):
    # Test template creation
    template1_data = {
        "name": "Test Template",
        "lang": TemplateLang.en,
    }
    response1 = client.post("/templates", json=template1_data)
    assert response1.status_code == 200
    template1 = response1.json()
    assert template1["name"] == template1_data["name"]
    assert template1["lang"] == template1_data["lang"]
    assert "id" in template1

    # Test getting single template
    response2 = client.get(f"/templates/{template1['id']}")
    assert response2.status_code == 200
    response2_data = response2.json()
    assert response2_data["id"] == template1["id"]
    assert response2_data["name"] == template1["name"]

    # Test getting all templates
    template2_data = {
        "name": "Test Template 2",
        "lang": TemplateLang.en,
    }
    response3 = client.post("/templates", json=template2_data)
    assert response3.status_code == 200
    template2 = response3.json()

    response4 = client.get("/templates")
    assert response4.status_code == 200
    data = response4.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    template_ids = [t["id"] for t in data]
    assert template1["id"] in template_ids
    assert template2["id"] in template_ids

    # Test template deletion
    response5 = client.delete(f"/templates/{template1['id']}")
    assert response5.status_code == 200
    response6 = client.get(f"/templates/{template2['id']}")
    assert response6.status_code == 200

    # Verify deletion
    response7 = client.get(f"/templates/{template1['id']}")
    assert response7.status_code == 404
    response8 = client.get(f"/templates/{template2['id']}")
    assert response8.status_code == 404


def test_generation_crud(client: TestClient):
    # First create a template
    template_data = {
        "name": "Test Template",
        "lang": TemplateLang.en,
    }
    response = client.post("/templates", json=template_data)
    template = response.json()

    # Test generation creation
    generation_data = {
        "name": "Test Generation",
        "method": "completion",
        "prompt": "This is a test prompt",
        "inputs": [],
    }
    response = client.post(
        f"/templates/{template['id']}/generations", json=generation_data
    )
    assert response.status_code == 200
    created_generation = response.json()
    assert created_generation["name"] == generation_data["name"]
    assert created_generation["method"] == generation_data["method"]
    assert created_generation["prompt"] == generation_data["prompt"]
    assert "id" in created_generation

    # Create output fields for the generation
    output_field_data1 = {
        "name": "output1",
        "type": "text",
        "description": "First output",
        "generation_id": created_generation["id"],
    }
    response = client.post(
        f"/templates/{template['id']}/fields", json=output_field_data1
    )
    assert response.status_code == 200
    output1 = response.json()

    output_field_data2 = {
        "name": "output2",
        "type": "text",
        "description": "Second output",
        "generation_id": created_generation["id"],
    }
    response = client.post(
        f"/templates/{template['id']}/fields", json=output_field_data2
    )
    assert response.status_code == 200
    output2 = response.json()

    # Test getting single generation and verify fields
    response = client.get(
        f"/templates/{template['id']}/generations/{created_generation['id']}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_generation["id"]
    assert data["name"] == created_generation["name"]
    assert data["template_id"] == template["id"]
    assert len(data["inputs"]) == 0
    assert len(data["outputs"]) == 2
    output_ids = {output["id"] for output in data["outputs"]}
    assert output1["id"] in output_ids
    assert output2["id"] in output_ids

    # Test updating generation
    update_data = {"name": "Updated Generation", "prompt": "Updated prompt"}
    response = client.patch(
        f"/templates/{template['id']}/generations/{created_generation['id']}",
        json=update_data,
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == update_data["name"]
    assert updated["prompt"] == update_data["prompt"]

    # Test updating output field
    field_update = {"description": "Updated output description"}
    response = client.patch(
        f"/templates/{template['id']}/fields/{output1['id']}", json=field_update
    )
    assert response.status_code == 200
    updated_field = response.json()
    assert updated_field["description"] == field_update["description"]

    # Verify field update through generation details
    response = client.get(
        f"/templates/{template['id']}/generations/{created_generation['id']}"
    )
    assert response.status_code == 200
    data = response.json()
    updated_outputs = {output["id"]: output for output in data["outputs"]}
    assert updated_outputs[output1["id"]]["description"] == field_update["description"]

    # Test generation deletion
    response = client.delete(
        f"/templates/{template['id']}/generations/{created_generation['id']}"
    )
    assert response.status_code == 200

    # Verify deletion
    response = client.get(
        f"/templates/{template['id']}/generations/{created_generation['id']}"
    )
    assert response.status_code == 404

    # Verify fields are deleted by checking generation details
    response = client.get(f"/templates/{template['id']}")
    assert response.status_code == 200
    template_data = response.json()
    field_ids = {field["id"] for field in template_data["fields"]}
    assert output1["id"] not in field_ids
    assert output2["id"] not in field_ids

    #  delete template
    response = client.delete(f"/templates/{template['id']}")
    assert response.status_code == 200


def test_generation_validation(client: TestClient):
    # Create a template first
    template_data = {
        "name": "Test Template",
        "lang": TemplateLang.EN,
    }
    response = client.post("/templates", json=template_data)
    template = response.json()

    # Test generation creation without prompt for completion method
    invalid_generation_data = {
        "name": "Test Generation",
        "method": "completion",
        "inputs": ["input1"],
        "outputs": [{"name": "output1", "type": "text"}],
    }
    response = client.post(
        f"/templates/{template['id']}/generations", json=invalid_generation_data
    )
    assert response.status_code == 422  # Validation error
