# Task Manager Lite

A simple, full-stack task management web application built with **FastAPI, Python, SQLAlchemy, and PostgreSQL**. Create, view, edit, complete, and delete tasks through a clean web interface.

🔗 **Live Demo:** https://task-manager-lite-hniy.onrender.com

## About

Task Manager Lite is a beginner-friendly full-stack project developed to understand the complete software development lifecycle, from building REST APIs and integrating a database to automated testing, version control, and cloud deployment.

The application uses FastAPI for its backend, HTML, CSS, and JavaScript for its frontend, and SQLAlchemy to support SQLite during local development and PostgreSQL in production.

## Features

- Create tasks with titles and descriptions
- View and manage all tasks
- Edit existing tasks
- Mark tasks as completed or incomplete
- Delete tasks
- RESTful API with request validation and error handling
- Database integration using SQLAlchemy
- Automated API tests using pytest
- Cloud deployment with Render
- PostgreSQL database hosted on Neon

## Tech Stack

| Category | Technologies |
|---|---|
| Language | Python |
| Backend | FastAPI, Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| Database | PostgreSQL, SQLite |
| ORM / Database Layer | SQLAlchemy |
| Testing | Pytest, HTTPX |
| Version Control | Git, GitHub |
| Deployment | Render |
| Database Hosting | Neon |

## Project Structure

```text
task-manager-lite/
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── test_main.py
├── README.md
├── .gitignore
├── static/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── tasks.db              # Local database, not committed
```

## Run Locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd task-manager-lite
```

Replace the placeholder with your actual GitHub repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Start the application

```bash
uvicorn main:app --reload
```

Open http://127.0.0.1:8000 in your browser.

Interactive API documentation is available at http://127.0.0.1:8000/docs.

## Database Configuration

The application uses SQLite by default for local development. To use PostgreSQL, configure the `DATABASE_URL` environment variable.

PowerShell example:

```powershell
$env:DATABASE_URL = "your-postgresql-connection-string"
uvicorn main:app --reload
```

**Security:** Never commit database credentials, passwords, or `.env` files to GitHub. Configure production secrets through your hosting provider's environment settings.

## Run Tests

Run the automated test suite:

```bash
python -m pytest -q
```

The tests cover the homepage, task creation, task listing, task updates, deletion, and validation and error-handling cases.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Serve the frontend |
| GET | `/health` | Health check |
| GET | `/api/tasks` | List tasks |
| POST | `/api/tasks` | Create a task |
| PUT | `/api/tasks/{task_id}` | Update a task |
| DELETE | `/api/tasks/{task_id}` | Delete a task |

## Deployment

The application is deployed on Render, with PostgreSQL hosted by Neon.

- **Live application:** https://task-manager-lite-hniy.onrender.com
- **Hosting:** Render
- **Database:** Neon PostgreSQL
- **Source code:** GitHub

The deployed service requires `DATABASE_URL` to be configured in its environment settings. Free hosting and database plans may have usage limits, inactivity delays, or database retention restrictions.

## Learning Outcomes

This project demonstrates practical experience with:

- Designing REST APIs using FastAPI
- Implementing CRUD operations
- Connecting an application to relational databases
- Managing configuration through environment variables
- Writing automated tests with pytest
- Using Git and GitHub for version control
- Deploying a Python web application to the cloud

## Future Improvements

- User registration and authentication
- Task priorities and due dates
- Search, filtering, and sorting
- Pagination
- Improved UI feedback and accessibility
- CI/CD with automated testing
- Database migrations using Alembic

## License

This project is available for learning and personal portfolio use. Add a license file if you intend to distribute it under a specific open-source license.
