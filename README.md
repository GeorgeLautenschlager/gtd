# gtd

Modern organization based on David Allen's GTD

This repository implements a minimal **FastAPI** application that serves as a "capture inbox" for a GTD workflow. The server is backed by **SQLite** and exposes a tiny frontend for entering and processing items.

## Quick start

1. **Install dependencies** (preferably in a virtualenv):
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```
3. Open http://localhost:8000/ in your browser to access the inbox UI.

## Project layout

```
./
├── main.py          # FastAPI application entrypoint
├── database.py      # SQLAlchemy engine/session setup
├── models.py        # ORM models
├── schemas.py       # Pydantic request/response models
├── static/          # frontend assets (index.html)
├── requirements.txt # Python dependencies
└── README.md
```

## API endpoints

| Method | Path                   | Description                        |
|--------|------------------------|------------------------------------|
| POST   | `/inbox`               | Create a new inbox item            |
| GET    | `/inbox`               | List unprocessed items (newest first) |
| POST   | `/inbox/{id}/process`  | Mark an item as processed          |
| GET    | `/inbox/all`           | List all items (for debugging)     |
| GET    | `/`                    | Serve the static HTML UI           |

The SQLite database file (`gtd.db`) is created in the workspace root on first run. Data persists between restarts.
