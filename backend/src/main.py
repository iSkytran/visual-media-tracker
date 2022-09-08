from datetime import datetime
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Any, Iterator, Union
import database
import models
import schemas

app = FastAPI(debug=True)
database.Base.metadata.create_all(database.engine)

undo_stack: list[tuple[str, str, Union[models.Show, models.Movie, models.Webcomic]]] = []
redo_stack: list[tuple[str, str, Union[models.Show, models.Movie, models.Webcomic]]] = []

def get_db() -> Iterator[Session]:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/shows", response_model=list[schemas.Show])
def get_shows(db: Session = Depends(get_db)) -> Any:
    shows = db.query(models.Show).all()
    return shows

@app.get("/movies", response_model=list[schemas.Movie])
def get_movies(db: Session = Depends(get_db)) -> Any:
    movies = db.query(models.Movie).all()
    return movies

@app.get("/webcomics", response_model=list[schemas.Webcomic])
def get_webcomics(db: Session = Depends(get_db)) -> Any:
    webcomics = db.query(models.Webcomic).all()
    return webcomics

@app.post("/shows")
def post_show(show: schemas.Show, db: Session = Depends(get_db)) -> Any:
    show.last_updated = datetime.now()
    show_item = models.Show(**show.dict())

    if show.id is None:
        new_show = db.merge(show_item)
        db.flush()
        undo_item = schemas.Show.from_orm(new_show)
        undo_stack.append(("delete", "show", undo_item))
    else:
        undo_item = schemas.Show.from_orm(db.query(models.Show).get(show.id))
        undo_stack.append(("revert", "show", undo_item))
        db.merge(show_item)

    db.commit()
    redo_stack.clear()

@app.post("/movies")
def post_movie(movie: schemas.Movie, db: Session = Depends(get_db)) -> Any:
    movie.last_updated = datetime.now()
    movie_item = models.Movie(**movie.dict())

    if movie.id is None:
        new_item = db.merge(movie_item)
        db.flush()
        undo_item = schemas.Movie.from_orm(new_item)
        undo_stack.append(("delete", "movie", undo_item))
    else:
        undo_item = schemas.Movie.from_orm(db.query(models.Movie).get(movie.id))
        undo_stack.append(("revert", "movie", undo_item))
        db.merge(movie_item)

    db.commit()
    redo_stack.clear()

@app.post("/webcomics")
def post_movie(webcomic: schemas.Webcomic, db: Session = Depends(get_db)) -> Any:
    webcomic.last_updated = datetime.now()
    webcomic_item = models.Webcomic(**webcomic.dict())

    if webcomic.id is None:
        new_item = db.merge(webcomic_item)
        db.flush()
        undo_item = schemas.Webcomic.from_orm(new_item)
        undo_stack.append(("delete", "webcomic", undo_item))
    else:
        undo_item = schemas.Webcomic.from_orm(db.query(models.Webcomic).get(webcomic.id))
        undo_stack.append(("revert", "webcomic", undo_item))
        db.merge(webcomic_item)

    db.commit()
    redo_stack.clear()

@app.delete("/shows/{show_id}")
def delete_show(show_id: int, db: Session = Depends(get_db)) -> None:
    delete_item = db.query(models.Show).get(show_id)

    undo_stack.append(("add", "show", schemas.Show.from_orm(delete_item)))

    db.delete(delete_item)
    db.commit()
    redo_stack.clear()

@app.delete("/movies/{movie_id}")

def delete_movie(movie_id: int, db: Session = Depends(get_db)) -> None:
    delete_item = db.query(models.Movie).get(movie_id)

    undo_stack.append(("add", "movie", schemas.Movie.from_orm(delete_item)))

    db.delete(delete_item)
    db.commit()
    redo_stack.clear()

@app.delete("/webcomics/{webcomic_id}")
def delete_webcomic(webcomic_id: int, db: Session = Depends(get_db)) -> None:
    delete_item = db.query(models.Webcomic).get(webcomic_id)

    undo_stack.append(("add", "webcomic", schemas.Webcomic.from_orm(delete_item)))

    db.delete(delete_item)
    db.commit()
    redo_stack.clear()

@app.post("/undo")
def undo(db: Session = Depends(get_db)) -> None:
    stack_operation(undo_stack, redo_stack, db)

@app.post("/redo")
def redo(db: Session = Depends(get_db)) -> None:
    stack_operation(redo_stack, undo_stack, db)

def stack_operation(stack: list[tuple[str, str, Union[models.Show, models.Movie, models.Webcomic]]],
                    reverse_stack: list[tuple[str, str, Union[models.Show, models.Movie, models.Webcomic]]],
                    db: Session):
    if not stack:
        return

    operation, media, obj = stack.pop()

    if operation == "add":
        if media == "show":
            new_show = db.merge(models.Show(**obj.dict()))
            db.flush()
            reverse_stack.append(("delete", "show", schemas.Show.from_orm(new_show)))
        elif media == "movie":
            new_movie = db.merge(models.Movie(**obj.dict()))
            db.flush()
            reverse_stack.append(("delete", "movie", schemas.Movie.from_orm(new_movie)))
        else:
            new_webcomic = db.merge(models.Webcomic(**obj.dict()))
            db.flush()
            reverse_stack.append(("delete", "webcomic", schemas.Webcomic.from_orm(new_webcomic)))
    elif operation == "revert":
        if media == "show":
            item = schemas.Show.from_orm(db.query(models.Show).get(obj.id))
            reverse_stack.append(("revert", "show", item))
            db.merge(models.Show(**obj.dict()))
        elif media == "movie":
            item = schemas.Movie.from_orm(db.query(models.Movie).get(obj.id))
            reverse_stack.append(("revert", "movie", item))
            db.merge(models.Movie(**obj.dict()))
        else:
            item = schemas.Webcomic.from_orm(db.query(models.Webcomic).get(obj.id))
            reverse_stack.append(("revert", "webcomic", item))
            db.merge(models.Webcomic(**obj.dict()))
    else:
        if media == "show":
            item = db.query(models.Show).get(obj.id)
            reverse_stack.append(("add", "show", schemas.Show.from_orm(item)))
            db.delete(item)
        elif media == "movie":
            item = db.query(models.Movie).get(obj.id)
            reverse_stack.append(("add", "movie", schemas.Movie.from_orm(item)))
            db.delete(item)
        else:
            item = db.query(models.Webcomic).get(obj.id)
            reverse_stack.append(("add", "webcomic", schemas.Webcomic.from_orm(item)))
            db.delete(item)

    db.commit()
