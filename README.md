# gtd

Modern organization based on David Allen's GTD

This repository implements a minimal **FastAPI** application that serves as a "capture inbox" for a GTD workflow. The server is backed by **SQLite** and exposes a tiny frontend for entering and processing items.

## Quick start

### Unix/macOS

1. **Install dependencies** (preferably in a virtualenv):
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```
3. Open http://localhost:8000/ in your browser to access the inbox UI.

### Windows (PowerShell)

1. **Create and activate a virtual environment** (optional but recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```powershell
   uvicorn main:app --reload
   ```
4. Point your browser to http://localhost:8000/ to use the inbox UI.

## Project layout

```
./
├── main.py              # FastAPI application entrypoint
├── database.py          # SQLAlchemy engine/session setup
├── models.py            # ORM models (InboxItem, Project, NextAction)
├── schemas.py           # Pydantic request/response models
├── crud.py              # Database operations for projects and actions
├── clarify.py           # Clarification logic and router
├── static/
│   ├── index.html       # Original inbox UI (Chunk 1)
│   └── clarify.html     # Clarification UI (Chunk 2)
├── requirements.txt     # Python dependencies
└── README.md
```

## API endpoints

### Inbox (Chunk 1)

| Method | Path                   | Description                        |
|--------|------------------------|------------------------------------|
| POST   | `/inbox`               | Create a new inbox item            |
| GET    | `/inbox`               | List unprocessed items (newest first) |
| POST   | `/inbox/{id}/process`  | Mark an item as processed          |
| GET    | `/inbox/all`           | List all items (for debugging)     |
| GET    | `/`                    | Serve the static HTML UI           |

### Clarification (Chunk 2)

| Method | Path                   | Description                        |
|--------|------------------------|------------------------------------|
| POST   | `/clarify`             | Process inbox item into project/action/other |
| GET    | `/clarify`             | Serve the clarification UI         |
| GET    | `/clarify/items`       | List unprocessed items for clarification |

### Projects (Chunk 2)

| Method | Path                   | Description                        |
|--------|------------------------|------------------------------------|
| GET    | `/projects`            | List active projects (filter by status=active/someday/completed) |
| GET    | `/projects/{id}`       | Get single project with its next actions |
| POST   | `/projects/{id}/complete` | Mark project as completed        |

### Next Actions (Chunk 2)

| Method | Path                   | Description                        |
|--------|------------------------|------------------------------------|
| GET    | `/next-actions`        | List active next actions (filter by ?context=phone) |
| POST   | `/next-actions/{id}/complete` | Mark next action as completed  |

The SQLite database file (`gtd.db`) is created in the workspace root on first run. Data persists between restarts.

## Features

### Chunk 1: Inbox Capture
- Capture unstructured items into inbox
- Mark items as processed
- Simple, focused capture interface

### Chunk 2: Clarification & Processing (NEW)
Process inbox items into one of five categories:

1. **Next Actions** - Single, specific physical steps
   - Context (phone, computer, work, home, self_care, home_exterior)
   - Energy required (high, medium, low)
   - Time estimate (optional)

2. **Projects** - Multi-step outcomes requiring multiple next actions
   - Project name and outcome description
   - Linked next actions
   - Active/someday/completed status

3. **Someday/Maybe** - Interesting but not now
   - Creates a project with someday status

4. **Reference** - Non-actionable but useful to keep
   - Marked as processed, retained for reference

5. **Trash** - Not actionable and not useful
   - Marked as processed, discarded
