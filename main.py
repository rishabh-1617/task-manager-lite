import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(
    os.getenv("TASK_MANAGER_DB_PATH", str(BASE_DIR / "tasks.db"))
)

# Use PostgreSQL when DATABASE_URL is configured.
# Otherwise, use SQLite for local development and testing.
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

_engines = {}


def get_engine():
    """Return the engine for the currently configured database."""
    if DATABASE_URL:
        url = DATABASE_URL
        connect_args = {}
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{DB_PATH.as_posix()}"
        connect_args = {"check_same_thread": False}

    if url not in _engines:
        _engines[url] = create_engine(
            url,
            connect_args=connect_args,
            pool_pre_ping=True,
        )

    return _engines[url]


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)


class TaskUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    completed: bool = False


def init_db():
    """Create the tasks table if it doesn't exist."""
    engine = get_engine()
    is_postgres = engine.dialect.name == "postgresql"

    id_column = (
        "SERIAL PRIMARY KEY"
        if is_postgres
        else "INTEGER PRIMARY KEY AUTOINCREMENT"
    )
    completed_column = "BOOLEAN" if is_postgres else "INTEGER"
    completed_default = "FALSE" if is_postgres else "0"

    with engine.begin() as connection:
        connection.execute(
            text(
                f"""
                CREATE TABLE IF NOT EXISTS tasks (
                    id {id_column},
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    completed {completed_column} NOT NULL DEFAULT {completed_default},
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )


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

    with get_engine().begin() as connection:
        result = connection.execute(
            text(
                """
                INSERT INTO tasks
                    (title, description, completed, created_at, updated_at)
                VALUES
                    (:title, :description, :completed, :created_at, :updated_at)
                RETURNING *
                """
            ),
            {
                "title": title,
                "description": description,
                "completed": False,
                "created_at": now,
                "updated_at": now,
            },
        )

        created_task = dict(result.mappings().one())

    return created_task


@app.get("/api/tasks")
def get_tasks():
    with get_engine().connect() as connection:
        result = connection.execute(
            text("SELECT * FROM tasks ORDER BY id DESC")
        )
        rows = result.mappings().all()

    return [dict(row) for row in rows]


@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    title = task.title.strip()

    if not title:
        raise HTTPException(
            status_code=422,
            detail="Task title cannot be empty.",
        )

    description = task.description.strip()
    now = datetime.now(timezone.utc).isoformat()

    with get_engine().begin() as connection:
        result = connection.execute(
            text(
                """
                UPDATE tasks
                SET title = :title,
                    description = :description,
                    completed = :completed,
                    updated_at = :updated_at
                WHERE id = :task_id
                """
            ),
            {
                "title": title,
                "description": description,
                "completed": task.completed,
                "updated_at": now,
                "task_id": task_id,
            },
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Task not found.",
            )

        updated_task = connection.execute(
            text("SELECT * FROM tasks WHERE id = :task_id"),
            {"task_id": task_id},
        ).mappings().one()

        updated_task = dict(updated_task)

    return updated_task


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with get_engine().begin() as connection:
        result = connection.execute(
            text("DELETE FROM tasks WHERE id = :task_id"),
            {"task_id": task_id},
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Task not found.",
            )