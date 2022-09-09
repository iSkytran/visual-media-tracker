from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

class Show(BaseModel):
    id: Optional[int]
    name: Optional[str]
    season: Optional[int]
    episode: Optional[int]
    status: Optional[str]
    date_started: Optional[date]
    date_finished: Optional[date]
    last_updated: Optional[datetime]

    class Config:
        orm_mode = True

class Movie(BaseModel):
    id: Optional[int]
    name: Optional[str]
    status: Optional[str]
    date_watched: Optional[date]
    last_updated: Optional[datetime]

    class Config:
        orm_mode = True

class Webcomic(BaseModel):
    id: Optional[int]
    name: Optional[str]
    last_updated: Optional[datetime]

    class Config:
        orm_mode = True
