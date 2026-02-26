from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite URL - relative file gtd.db in workspace root
SQLALCHEMY_DATABASE_URL = "sqlite:///./gtd.db"

# connect_args needed for SQLite to allow multithreaded access
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
