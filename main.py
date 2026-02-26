from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, engine

# create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


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


@app.get("/", response_class=HTMLResponse)
def read_root():
    # simple static HTML front-end
    with open("static/index.html", "r") as f:
        return f.read()
