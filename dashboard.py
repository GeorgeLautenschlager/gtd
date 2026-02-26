from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import crud
import schemas
from database import SessionLocal

router = APIRouter(prefix="/api", tags=["dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    stats = crud.dashboard_stats(db)
    return stats


@router.get("/next-actions/smart", response_model=list[schemas.ActionWithProject])
def get_smart_actions(
    context: str | None = Query(None),
    time_available: int | None = Query(None),
    energy: str | None = Query(None),
    has_project: bool | None = Query(None),
    limit: int = Query(50, le=50),
    db: Session = Depends(get_db),
):
    raw = crud.smart_next_actions(db, context=context, time_available=time_available, energy=energy, has_project=has_project, limit=limit)
    results: list[schemas.ActionWithProject] = []
    for item in raw:
        a = item["action"]
        proj = item["project"]
        resp = schemas.ActionWithProject.from_orm(a)
        resp.project_name = proj.name if proj else None
        resp.project_outcome = proj.outcome_description if proj else None
        results.append(resp)
    return results


@router.get("/contexts", response_model=dict)
def list_contexts(db: Session = Depends(get_db)):
    stats = crud.dashboard_stats(db)
    return stats["by_context"]


@router.get("/review/stale", response_model=list[schemas.ActionWithProject])
def review_stale(days: int = 7, db: Session = Depends(get_db)):
    stale = crud.list_stale_actions(db, days=days)
    results: list[schemas.ActionWithProject] = []
    for a in stale:
        proj = None
        if a.project_id:
            proj = db.query(__import__('models').Project).filter(__import__('models').Project.id == a.project_id).first()
        resp = schemas.ActionWithProject.from_orm(a)
        resp.project_name = proj.name if proj else None
        resp.project_outcome = proj.outcome_description if proj else None
        results.append(resp)
    return results
