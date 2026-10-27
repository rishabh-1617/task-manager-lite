import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

# Use a configured database path when provided.
# Otherwise, use tasks.db in the project directory.
DB_PATH = Path(
    os.getenv("TASK_MANAGER_DB_PATH", str(BASE_DIR / "tasks.db"))
)


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)


class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    completed: bool = False


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    """Create the tasks table if it doesn't exist."""
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                completed INTEGER NOT NULL DEFAULT 0
                    CHECK (completed IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


# Initialize the database and table.
init_db()


app = FastAPI(
    title="Task Manager API",
    description="A beginner-friendly task management API.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def serve_homepage():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/tasks", status_code=201)
def create_task(task: TaskCreate):
    title = task.title.strip()

    if not title:
        raise HTTPException(
            status_code=422,
            detail="Task title cannot be empty.",
        )

    description = task.description.strip()
    now = datetime.now(timezone.utc).isoformat()

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.execute(
            """
            INSERT INTO tasks (title, description, completed, created_at, updated_at)
            VALUES (?, ?, 0, ?, ?)
            """,
            (title, description, now, now),
        )

        connection.commit()

        created_task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

        return dict(created_task)
    
    finally:
        connection.close()


@app.get("/api/tasks")
def get_tasks():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    title = task.title.strip()

    if not title:
        raise HTTPException(
            status_code=422,
            detail="Task title cannot be empty.",
        )

    description = task.description.strip()
    completed = int(task.completed)
    now = datetime.now(timezone.utc).isoformat()

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET title = ?,
                description = ?,
                completed = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (title, description, completed, now, task_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Task not found.",
            )

        connection.commit()

        updated_task = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(updated_task)

    finally:
        connection.close()


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Task not found.",
            )

        connection.commit()

    finally:
        connection.close()
