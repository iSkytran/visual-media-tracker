from sqlalchemy import Column, Integer, String, Date, DateTime
from database import Base

class Show(Base):
    __tablename__ = "shows"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    season = Column(Integer)
    episode = Column(Integer)
    status = Column(String)
    date_started = Column(Date)
    date_finished = Column(Date)
    last_updated = Column(DateTime)

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(String)
    date_watched = Column(Date)
    last_updated = Column(DateTime)

class Webcomic(Base):
    __tablename__ = "webcomics"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    last_updated = Column(DateTime)

