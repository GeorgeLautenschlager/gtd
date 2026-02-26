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
