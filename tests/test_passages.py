from fastapi.testclient import TestClient

example_url = "https://example.com/"


def test_passage_crud(client: TestClient):
    # Test creating a passage
    response = client.post(f"/passages?url={example_url}")
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == example_url
    assert "title" in data
    assert "content" in data
    assert "id" in data
    passage_id = data["id"]

    # Test getting all passages
    response = client.get("/passages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "title" in data[0]
    assert "url" in data[0]

    # Test getting single passage
    response = client.get(f"/passages/{passage_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == passage_id
    assert data["url"] == example_url
    assert "title" in data
    assert "content" in data

    # Test creating a note for the passage
    note_data = {
        "selected_text": "test text",
        "context": "This is a test context",
        "paragraph_index": 0,
        "start_index": 0,
        "end_index": 4,
    }

    response = client.post(f"/passages/{passage_id}/notes", json=note_data)
    assert response.status_code == 200
    data = response.json()
    assert data["passage_id"] == passage_id
    assert data["selected_text"] == note_data["selected_text"]
    assert data["context"] == note_data["context"]
    assert "content" in data
    assert "id" in data

    # delete the passage
    response = client.delete(f"/passages/{passage_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Passage deleted successfully"}

    # verify the passage is deleted
    response = client.get(f"/passages/{passage_id}")
    assert response.status_code == 404
