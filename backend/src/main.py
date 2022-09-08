from datetime import datetime
from fastapi import FastAPI, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Any, Iterator
import database
import schemas

app = FastAPI()

async def get_db() -> Iterator[Session]:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/shows")
async def get_shows(db: Session = Depends(get_db)) -> Any:
    shows = db.query(database.Show).all()
    return jsonable_encoder(shows)

@app.get("/movies")
async def get_movies(db: Session = Depends(get_db)) -> Any:
    movies = db.query(database.Movie).all()
    return jsonable_encoder(movies)

@app.get("/webcomics")
async def get_webcomics(db: Session = Depends(get_db)) -> Any:
    webcomics = db.query(database.Webcomic).all()
    return jsonable_encoder(webcomics)

@app.post("/shows")
async def post_show(show: schemas.Show, db: Session = Depends(get_db)) -> Any:
    show_item = database.Show(**show.dict(), last_updated=datetime.now())
    db.merge(show_item)
    db.commit()
    return jsonable_encoder(show)

@app.post("/movies")
async def post_movie(movie: schemas.Movie, db: Session = Depends(get_db)) -> Any:
    movie_item = database.Movie(**movie.dict(), last_updated=datetime.now())
    db.merge(movie_item)
    db.commit()
    return jsonable_encoder(movie)

@app.post("/webcomics")
async def post_movie(webcomic: schemas.Webcomic, db: Session = Depends(get_db)) -> Any:
    webcomic_item = database.Webcomic(**webcomic.dict(), last_updated=datetime.now())
    db.merge(webcomic_item)
    db.commit()
    return jsonable_encoder(webcomic)
