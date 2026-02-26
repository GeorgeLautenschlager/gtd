from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
import schemas
import crud
from clarify import router as clarify_router
from dashboard import router as dashboard_router
from review import router as review_router
from database import SessionLocal, engine

# create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# include routers
app.include_router(clarify_router)
app.include_router(dashboard_router)
app.include_router(review_router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/inbox", response_model=schemas.InboxItemResponse)
def create_item(item: schemas.InboxItemCreate, db: Session = Depends(get_db)):
    db_item = models.InboxItem(content=item.content)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/inbox", response_model=list[schemas.InboxItemResponse])
def list_unprocessed(db: Session = Depends(get_db)):
    items = (
        db.query(models.InboxItem)
        .filter_by(processed=False)
        .order_by(models.InboxItem.created_at.desc())
        .all()
    )
    return items


@app.post("/inbox/{item_id}/process", response_model=schemas.InboxItemResponse)
def process_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.InboxItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not item.processed:
        item.processed = True
        item.processed_at = datetime.utcnow()
        db.add(item)
        db.commit()
        db.refresh(item)
    return item


@app.get("/inbox/all", response_model=list[schemas.InboxItemResponse])
def list_all(db: Session = Depends(get_db)):
    items = db.query(models.InboxItem).order_by(models.InboxItem.created_at.desc()).all()
    return items


# Projects endpoints
@app.get("/projects", response_model=list[schemas.ProjectResponse])
def list_projects(status: str = "active", db: Session = Depends(get_db)):
    projects = crud.list_projects(db, status=status)
    return projects


@app.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/projects/{project_id}/complete", response_model=schemas.ProjectResponse)
def complete_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.complete_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# Next Actions endpoints
@app.get("/next-actions", response_model=list[schemas.NextActionResponse])
def list_next_actions(context: str | None = None, db: Session = Depends(get_db)):
    actions = crud.list_next_actions(db, context=context)
    return actions


@app.post("/next-actions/{action_id}/complete", response_model=schemas.NextActionResponse)
def complete_next_action(action_id: int, db: Session = Depends(get_db)):
    action = crud.complete_next_action(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Next action not found")
    return action


@app.get("/", response_class=HTMLResponse)
def read_root():
    # simple static HTML front-end
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/clarify", response_class=HTMLResponse)
def read_clarify():
    # clarification UI
    with open("static/clarify.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard():
    # dashboard UI
    with open("static/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/review", response_class=HTMLResponse)
def read_review():
    with open("static/review.html", "r", encoding="utf-8") as f:
        return f.read()
