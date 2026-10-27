
import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Create a separate database file for this test.
    test_db_path = tmp_path / "test_tasks.db"

    # Redirect the app to the temporary database.
    monkeypatch.setattr(main, "DB_PATH", test_db_path)

    # Create the schema in the temporary database.
    main.init_db()

    # Provide a test client.
    with TestClient(main.app) as test_client:
        yield test_client


def test_homepage(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Task Manager Lite" in response.text


def test_create_task(client):
    response = client.post(
        "/api/tasks",
        json={
            "title": "Learn pytest",
            "description": "Test task creation",
        },
    )

    assert response.status_code == 201

    task = response.json()
    assert task["id"] > 0
    assert task["title"] == "Learn pytest"
    assert task["description"] == "Test task creation"
    assert task["completed"] == 0


def test_list_tasks(client):
    # Create a task first.
    client.post(
        "/api/tasks",
        json={
            "title": "Test database",
            "description": "Verify task listing",
        },
    )

    # Retrieve tasks from the API.
    response = client.get("/api/tasks")

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Test database"
    assert tasks[0]["description"] == "Verify task listing"


def test_update_task(client):
    # Create a task.
    create_response = client.post(
        "/api/tasks",
        json={
            "title": "Original title",
            "description": "Original description",
        },
    )

    task_id = create_response.json()["id"]

    # Update the task.
    update_response = client.put(
        f"/api/tasks/{task_id}",
        json={
            "title": "Updated title",
            "description": "Updated description",
            "completed": True,
        },
    )

    assert update_response.status_code == 200

    updated_task = update_response.json()
    assert updated_task["title"] == "Updated title"
    assert updated_task["description"] == "Updated description"
    assert bool(updated_task["completed"]) is True


def test_delete_task(client):
    # Create a task.
    create_response = client.post(
        "/api/tasks",
        json={
            "title": "Task to delete",
            "description": "Temporary test task",
        },
    )

    task_id = create_response.json()["id"]

    # Delete the task.
    delete_response = client.delete(f"/api/tasks/{task_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # Verify the task is gone.
    list_response = client.get("/api/tasks")

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_create_task_with_empty_title(client):
    response = client.post(
        "/api/tasks",
        json={
            "title": "   ",
            "description": "Invalid task",
        },
    )

    assert response.status_code == 422


def test_create_task_with_missing_title(client):
    response = client.post(
        "/api/tasks",
        json={
            "description": "Title is missing",
        },
    )

    assert response.status_code == 422


def test_update_nonexistent_task(client):
    response = client.put(
        "/api/tasks/99999",
        json={
            "title": "Updated title",
            "description": "Updated description",
            "completed": True,
        },
    )

    assert response.status_code == 404


def test_delete_nonexistent_task(client):
    response = client.delete("/api/tasks/99999")

    assert response.status_code == 404

