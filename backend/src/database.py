from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///visual-media-tracker.db")
SessionLocal = sessionmaker(bind=engine)
