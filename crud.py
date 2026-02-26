from datetime import datetime
from sqlalchemy.orm import Session
import models
import schemas


# Projects
def create_project(db: Session, project: schemas.ProjectCreate) -> models.Project:
    db_project = models.Project(
        name=project.name,
        outcome_description=project.outcome_description,
        status=project.status
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project(db: Session, project_id: int) -> models.Project | None:
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def list_projects(db: Session, status: str = "active") -> list[models.Project]:
    return db.query(models.Project).filter(models.Project.status == status).order_by(models.Project.created_at.desc()).all()


def complete_project(db: Session, project_id: int) -> models.Project | None:
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project:
        project.status = "completed"
        project.completed_at = datetime.utcnow()
        db.add(project)
        db.commit()
        db.refresh(project)
    return project


# Next Actions
def create_next_action(db: Session, action: schemas.NextActionCreate) -> models.NextAction:
    db_action = models.NextAction(
        project_id=action.project_id,
        description=action.description,
        context=action.context,
        energy_required=action.energy_required,
        time_estimate=action.time_estimate
    )
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action


def get_next_action(db: Session, action_id: int) -> models.NextAction | None:
    return db.query(models.NextAction).filter(models.NextAction.id == action_id).first()


def list_next_actions(db: Session, context: str | None = None, status: str = "active") -> list[models.NextAction]:
    query = db.query(models.NextAction).filter(models.NextAction.status == status)
    if context:
        query = query.filter(models.NextAction.context == context)
    return query.order_by(models.NextAction.created_at.desc()).all()


def complete_next_action(db: Session, action_id: int) -> models.NextAction | None:
    action = db.query(models.NextAction).filter(models.NextAction.id == action_id).first()
    if action:
        action.status = "completed"
        action.completed_at = datetime.utcnow()
        db.add(action)
        db.commit()
        db.refresh(action)
    return action


# Inbox Items
def get_inbox_item(db: Session, item_id: int) -> models.InboxItem | None:
    return db.query(models.InboxItem).filter(models.InboxItem.id == item_id).first()


def update_inbox_item_processed(db: Session, item_id: int, clarified_result_type: str) -> models.InboxItem | None:
    item = db.query(models.InboxItem).filter(models.InboxItem.id == item_id).first()
    if item:
        item.processed = True
        item.processed_at = datetime.utcnow()
        item.clarified_result_type = clarified_result_type
        db.add(item)
        db.commit()
        db.refresh(item)
    return item


# Dashboard helpers
def dashboard_stats(db: Session) -> dict:
    total_active = db.query(models.NextAction).filter(models.NextAction.status == "active").count()

    # by_context
    contexts = ["phone", "computer", "work", "home", "self_care", "home_exterior"]
    by_context = {}
    for c in contexts:
        by_context[c] = db.query(models.NextAction).filter(models.NextAction.status == "active", models.NextAction.context == c).count()

    # by_energy
    energies = ["high", "medium", "low"]
    by_energy = {}
    for e in energies:
        by_energy[e] = db.query(models.NextAction).filter(models.NextAction.status == "active", models.NextAction.energy_required == e).count()

    # stale actions > 7 days
    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(days=7)
    stale_count = db.query(models.NextAction).filter(models.NextAction.status == "active", models.NextAction.created_at <= cutoff).count()

    inbox_count = db.query(models.InboxItem).filter(models.InboxItem.processed == False).count()

    active_projects = db.query(models.Project).filter(models.Project.status == "active").count()

    return {
        "total_active_actions": total_active,
        "by_context": by_context,
        "by_energy": by_energy,
        "stale_actions": stale_count,
        "inbox_count": inbox_count,
        "active_projects": active_projects,
    }


def list_stale_actions(db: Session, days: int = 7, limit: int = 100) -> list[models.NextAction]:
    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(models.NextAction)
        .filter(models.NextAction.status == "active", models.NextAction.created_at <= cutoff)
        .order_by(models.NextAction.created_at.asc())
        .limit(limit)
        .all()
    )


def smart_next_actions(db: Session, context: str | None = None, time_available: int | None = None, energy: str | None = None, has_project: bool | None = None, limit: int = 50) -> list[dict]:
    # Fetch candidate actions (active)
    query = db.query(models.NextAction).filter(models.NextAction.status == "active")
    if context:
        query = query.filter(models.NextAction.context == context)
    if has_project is True:
        query = query.filter(models.NextAction.project_id.isnot(None))
    if has_project is False:
        query = query.filter(models.NextAction.project_id.is_(None))

    candidates = query.order_by(models.NextAction.created_at.asc()).limit(500).all()

    scored = []
    from datetime import datetime

    for a in candidates:
        score = 0
        # energy match
        if energy and a.energy_required == energy:
            score += 3
        # time fit
        if time_available is not None and a.time_estimate is not None and a.time_estimate <= time_available:
            score += 2
        # project-linked
        if a.project_id:
            # bonus only if project active
            proj = db.query(models.Project).filter(models.Project.id == a.project_id).first()
            if proj and proj.status == "active":
                score += 1
        # age bonus: +1 per day old
        age_days = (datetime.utcnow() - a.created_at).days if a.created_at else 0
        score += age_days

        scored.append({"action": a, "score": score, "age_days": age_days})

    # sort by score desc, created_at asc
    scored.sort(key=lambda x: (-x["score"], x["action"].created_at))

    # trim and attach project info
    results = []
    for entry in scored[:limit]:
        a = entry["action"]
        proj = None
        if a.project_id:
            proj = db.query(models.Project).filter(models.Project.id == a.project_id).first()
        results.append(
            {
                "action": a,
                "score": entry["score"],
                "age_days": entry["age_days"],
                "project": proj,
            }
        )

    return results


### Review session CRUD
def create_review_session(db: Session) -> models.ReviewSession:
    # Create session and generate checklist items based on current data
    session = models.ReviewSession()
    db.add(session)
    db.commit()
    db.refresh(session)

    items: list[models.ReviewChecklistItem] = []

    # Inbox
    inbox_count = db.query(models.InboxItem).filter(models.InboxItem.processed == False).count()
    items.append(models.ReviewChecklistItem(review_session_id=session.id, category='inbox', item_text='Inbox zero (process all unprocessed items)'))

    # Projects: one or two checks per active project
    projects = db.query(models.Project).filter(models.Project.status == 'active').all()
    for p in projects:
        items.append(models.ReviewChecklistItem(review_session_id=session.id, category='projects', item_text=f'Review: {p.name} — any new next actions needed?'))
        items.append(models.ReviewChecklistItem(review_session_id=session.id, category='projects', item_text=f'Review: {p.name} — project still relevant?'))

    # Waiting
    items.append(models.ReviewChecklistItem(review_session_id=session.id, category='waiting', item_text='Review waiting-for list — any follow-ups needed?'))
    items.append(models.ReviewChecklistItem(review_session_id=session.id, category='waiting', item_text='Check stale waiting items (> 1 week)'))

    # Someday
    items.append(models.ReviewChecklistItem(review_session_id=session.id, category='someday', item_text='Review someday/maybe — anything to activate?'))
    items.append(models.ReviewChecklistItem(review_session_id=session.id, category='someday', item_text='Prune obsolete ideas'))

    # Clean
    items.append(models.ReviewChecklistItem(review_session_id=session.id, category='clean', item_text='Clean up completed items archive'))
    items.append(models.ReviewChecklistItem(review_session_id=session.id, category='clean', item_text='Verify next actions are truly next (not dependent)'))

    # Goals
    items.append(models.ReviewChecklistItem(review_session_id=session.id, category='goals', item_text='Review calendar (past week) — capture anything missed'))
    items.append(models.ReviewChecklistItem(review_session_id=session.id, category='goals', item_text='Review calendar (next 2 weeks) — upcoming deadlines?'))
    items.append(models.ReviewChecklistItem(review_session_id=session.id, category='goals', item_text='Check against 1-2 year goals — alignment?'))

    db.add_all(items)
    db.commit()
    # refresh and return session with items
    db.refresh(session)
    return session


def get_review_session(db: Session, session_id: int) -> models.ReviewSession | None:
    return db.query(models.ReviewSession).filter(models.ReviewSession.id == session_id).first()


def list_review_checklist(db: Session, session_id: int) -> list[models.ReviewChecklistItem]:
    return db.query(models.ReviewChecklistItem).filter(models.ReviewChecklistItem.review_session_id == session_id).order_by(models.ReviewChecklistItem.id.asc()).all()


def complete_checklist_item(db: Session, session_id: int, item_id: int, notes: str | None = None) -> models.ReviewChecklistItem | None:
    item = db.query(models.ReviewChecklistItem).filter(models.ReviewChecklistItem.review_session_id == session_id, models.ReviewChecklistItem.id == item_id).first()
    if item:
        item.completed = True
        item.completed_at = datetime.utcnow()
        if notes:
            item.notes = notes
        db.add(item)
        db.commit()
        db.refresh(item)
    return item


def complete_review_session(db: Session, session_id: int, notes: str | None = None) -> models.ReviewSession | None:
    session = db.query(models.ReviewSession).filter(models.ReviewSession.id == session_id).first()
    if session:
        session.completed_at = datetime.utcnow()
        if session.started_at:
            session.duration_minutes = int((session.completed_at - session.started_at).total_seconds() / 60)
        if notes:
            session.notes = notes
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def review_stats(db: Session) -> dict:
    total = db.query(models.ReviewSession).count()
    completed_sessions = db.query(models.ReviewSession).filter(models.ReviewSession.completed_at.isnot(None)).all()
    avg = None
    if completed_sessions:
        durations = [s.duration_minutes for s in completed_sessions if s.duration_minutes]
        if durations:
            avg = int(sum(durations) / len(durations))

    # streak: consecutive weeks with at least one completed review
    from datetime import datetime, timedelta
    last_completed = db.query(models.ReviewSession).filter(models.ReviewSession.completed_at.isnot(None)).order_by(models.ReviewSession.completed_at.desc()).first()
    last_dt = last_completed.completed_at if last_completed else None

    # compute current streak (simple approach: count backwards week-by-week)
    streak = 0
    if last_dt:
        now = datetime.utcnow()
        week_start = last_dt - timedelta(days=last_dt.weekday()+1)  # approximate
        # iterate backwards
        check_dt = last_dt
        while True:
            week_end = check_dt
            week_start = week_end - timedelta(days=7)
            found = db.query(models.ReviewSession).filter(models.ReviewSession.completed_at >= week_start, models.ReviewSession.completed_at <= week_end).count()
            if found:
                streak += 1
                check_dt = week_start - timedelta(seconds=1)
            else:
                break

    return {
        'total_sessions': total,
        'average_duration': avg,
        'current_streak_weeks': streak,
        'last_completed': last_dt,
    }


def last_review(db: Session):
    return db.query(models.ReviewSession).filter(models.ReviewSession.completed_at.isnot(None)).order_by(models.ReviewSession.completed_at.desc()).first()
