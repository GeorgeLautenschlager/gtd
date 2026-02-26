from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class InboxItem(Base):
    __tablename__ = "inbox_items"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    clarified_result_type = Column(String, nullable=True)  # next_action, project, trash, reference, someday_maybe


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    outcome_description = Column(String, nullable=False)
    status = Column(String, default="active")  # active, someday, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    next_actions = relationship("NextAction", back_populates="project")


class NextAction(Base):
    __tablename__ = "next_actions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    description = Column(String, nullable=False)
    context = Column(String, nullable=False)  # phone, computer, work, home, self_care, home_exterior
    energy_required = Column(String, nullable=False)  # high, medium, low
    time_estimate = Column(Integer, nullable=True)  # in minutes
    status = Column(String, default="active")  # active, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="next_actions")


class ReviewSession(Base):
    __tablename__ = "review_sessions"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)

    checklist_items = relationship("ReviewChecklistItem", back_populates="session")


class ReviewChecklistItem(Base):
    __tablename__ = "review_checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    review_session_id = Column(Integer, ForeignKey("review_sessions.id"), nullable=False)
    category = Column(String, nullable=False)  # inbox, projects, waiting, someday, clean, goals
    item_text = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)

    session = relationship("ReviewSession", back_populates="checklist_items")
