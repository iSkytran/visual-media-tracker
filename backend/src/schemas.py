from datetime import date
from typing import Optional
from pydantic import BaseModel

class Show(BaseModel):
    id: Optional[int]
    name: str
    season: Optional[int]
    episode: Optional[int]
    status: str
    date_started: Optional[date]
    date_finished: Optional[date]

    class Config:
        orm_mode = True

class Movie(BaseModel):
    id: Optional[int]
    name: str
    status: str
    date_watched: Optional[date]

    class Config:
        orm_mode = True

class Webcomic(BaseModel):
    id: Optional[int]
    name: str

    class Config:
        orm_mode = True
