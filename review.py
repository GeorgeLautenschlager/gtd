from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
from database import SessionLocal

router = APIRouter(prefix="/api/review", tags=["review"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/start", response_model=schemas.ReviewSessionStart)
def start_review(db: Session = Depends(get_db)):
    session = crud.create_review_session(db)
    items = crud.list_review_checklist(db, session.id)
    items_payload = []
    for i in items:
        items_payload.append({
            "id": i.id,
            "category": i.category,
            "item_text": i.item_text,
            "completed": bool(i.completed),
            "completed_at": i.completed_at,
            "notes": i.notes,
        })
    return {"id": session.id, "started_at": session.started_at, "checklist_items": items_payload}


@router.get("/session/{session_id}", response_model=schemas.ReviewSessionStart)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = crud.get_review_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Review session not found")
    items = crud.list_review_checklist(db, session.id)
    items_payload = []
    for i in items:
        items_payload.append({
            "id": i.id,
            "category": i.category,
            "item_text": i.item_text,
            "completed": bool(i.completed),
            "completed_at": i.completed_at,
            "notes": i.notes,
        })
    return {"id": session.id, "started_at": session.started_at, "checklist_items": items_payload}


@router.post("/session/{session_id}/item/{item_id}/complete", response_model=schemas.ReviewChecklistItemResponse)
def complete_item(session_id: int, item_id: int, notes: dict | None = None, db: Session = Depends(get_db)):
    n = None
    if notes and isinstance(notes, dict):
        n = notes.get('notes')
    item = crud.complete_checklist_item(db, session_id, item_id, notes=n)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    return {
        "id": item.id,
        "category": item.category,
        "item_text": item.item_text,
        "completed": bool(item.completed),
        "completed_at": item.completed_at,
        "notes": item.notes,
    }


@router.post("/session/{session_id}/complete", response_model=schemas.ReviewSessionStart)
def complete_review(session_id: int, payload: schemas.ReviewCompleteRequest, db: Session = Depends(get_db)):
    session = crud.complete_review_session(db, session_id, notes=payload.notes)
    if not session:
        raise HTTPException(status_code=404, detail="Review session not found")
    items = crud.list_review_checklist(db, session.id)
    items_payload = []
    for i in items:
        items_payload.append({
            "id": i.id,
            "category": i.category,
            "item_text": i.item_text,
            "completed": bool(i.completed),
            "completed_at": i.completed_at,
            "notes": i.notes,
        })
    return {"id": session.id, "started_at": session.started_at, "checklist_items": items_payload}


@router.get("/stats", response_model=schemas.ReviewStats)
def stats(db: Session = Depends(get_db)):
    s = crud.review_stats(db)
    return s


@router.get("/last", response_model=schemas.ReviewSessionStart | None)
def last(db: Session = Depends(get_db)):
    s = crud.last_review(db)
    if not s:
        return None
    items = crud.list_review_checklist(db, s.id)
    items_payload = []
    for i in items:
        items_payload.append({
            "id": i.id,
            "category": i.category,
            "item_text": i.item_text,
            "completed": bool(i.completed),
            "completed_at": i.completed_at,
            "notes": i.notes,
        })
    return {"id": s.id, "started_at": s.started_at, "checklist_items": items_payload}
