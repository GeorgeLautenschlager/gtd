from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
from database import SessionLocal


router = APIRouter(prefix="/clarify", tags=["clarify"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=dict)
def clarify_item(clarify_req: schemas.ClarifyRequest, db: Session = Depends(get_db)):
    """
    Process an inbox item into a project, next action, or other category.

    Actions:
    - "next_action": Create a single next_action
    - "project": Create a project with its first next_action
    - "trash": Mark as processed, no further action
    - "reference": Mark as processed, stored for reference
    - "someday": Create a project with status="someday"
    """

    # Validate inbox item exists and is unprocessed
    inbox_item = crud.get_inbox_item(db, clarify_req.inbox_item_id)
    if not inbox_item:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    if inbox_item.processed:
        raise HTTPException(status_code=400, detail="Inbox item already processed")

    result = {"inbox_item_id": clarify_req.inbox_item_id}

    if clarify_req.action == "next_action":
        if not clarify_req.next_action_data:
            raise HTTPException(status_code=400, detail="next_action_data required")

        action = crud.create_next_action(db, clarify_req.next_action_data)
        crud.update_inbox_item_processed(db, inbox_item.id, "next_action")
        result["next_action"] = schemas.NextActionResponse.from_orm(action)

    elif clarify_req.action == "project":
        if not clarify_req.project_data or not clarify_req.next_action_data:
            raise HTTPException(status_code=400, detail="project_data and next_action_data required")

        # Create project
        project = crud.create_project(db, clarify_req.project_data)

        # Create first next action linked to project
        action_data = clarify_req.next_action_data
        action_data.project_id = project.id
        action = crud.create_next_action(db, action_data)

        crud.update_inbox_item_processed(db, inbox_item.id, "project")
        result["project"] = schemas.ProjectResponse.from_orm(project)
        result["first_action"] = schemas.NextActionResponse.from_orm(action)

    elif clarify_req.action == "someday":
        if not clarify_req.project_data:
            raise HTTPException(status_code=400, detail="project_data required")

        project_data = clarify_req.project_data
        project_data.status = "someday"
        project = crud.create_project(db, project_data)
        crud.update_inbox_item_processed(db, inbox_item.id, "someday_maybe")
        result["project"] = schemas.ProjectResponse.from_orm(project)

    elif clarify_req.action == "trash":
        crud.update_inbox_item_processed(db, inbox_item.id, "trash")

    elif clarify_req.action == "reference":
        crud.update_inbox_item_processed(db, inbox_item.id, "reference")

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {clarify_req.action}")

    return result


@router.get("/items", response_model=list[schemas.InboxItemResponse])
def get_unprocessed_items(db: Session = Depends(get_db)):
    """Get unprocessed inbox items for clarification."""
    items = (
        db.query(__import__('models').InboxItem)
        .filter_by(processed=False)
        .order_by(__import__('models').InboxItem.created_at.desc())
        .all()
    )
    return items
