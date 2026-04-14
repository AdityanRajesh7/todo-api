import pytest
from fastapi.testclient import TestClient
from app.main import app, tasks

# ── Fixture ───────────────────────────────────────────────────
# Runs before every test. Clears the in-memory store so each
# test starts with a clean slate — no leftover data from others.

@pytest.fixture(autouse=True)
def clear_tasks():
    tasks.clear()
    yield                  # test runs here
    tasks.clear()          # cleanup after too, just in case

client = TestClient(app)

# ── Helper ────────────────────────────────────────────────────

def create_task(title="Test task", done=False):
    """Reusable shortcut so tests stay readable."""
    return client.post("/tasks", json={"title": title, "done": done})

# ── Tests ─────────────────────────────────────────────────────

def test_list_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 999
    assert response.json() == []

def test_create_task_returns_201():
    response = create_task("Learn FastAPI")
    assert response.status_code == 201

def test_create_task_has_correct_fields():
    response = create_task("Learn FastAPI")
    data = response.json()
    assert data["title"] == "Learn FastAPI"
    assert data["done"] == False
    assert "id" in data          # UUID was generated

def test_list_tasks_after_creating():
    create_task("Task A")
    create_task("Task B")
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_task_by_id():
    created = create_task("Find me").json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Find me"

def test_get_task_not_found():
    response = client.get("/tasks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404

def test_update_task():
    created = create_task("Old title").json()
    response = client.put(
        f"/tasks/{created['id']}",
        json={"title": "New title", "done": True}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["done"] == True

def test_delete_task():
    created = create_task("Delete me").json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 204

def test_delete_task_then_get_returns_404():
    created = create_task("Gone").json()
    client.delete(f"/tasks/{created['id']}")
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 404

def test_create_task_missing_title_returns_422():
    # FastAPI's validation should reject this automatically
    response = client.post("/tasks", json={"done": False})
    assert response.status_code == 422