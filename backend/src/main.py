from datetime import datetime
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import Any, Iterator, Type
from types import ModelTypes, SchemaTypes, OperationStackType
import database
import models
import schemas

app = FastAPI(debug=True)
database.Base.metadata.create_all(database.engine)

undo_stack: OperationStackType = []
redo_stack: OperationStackType = []

def get_db() -> Iterator[Session]:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/shows", response_model=list[schemas.Show])
def get_shows(db: Session = Depends(get_db)) -> Any:
    return db.query(models.Show).all()

@app.get("/movies", response_model=list[schemas.Movie])
def get_movies(db: Session = Depends(get_db)) -> Any:
    return db.query(models.Movie).all()

@app.get("/webcomics", response_model=list[schemas.Webcomic])
def get_webcomics(db: Session = Depends(get_db)) -> Any:
    return db.query(models.Webcomic).all()

@app.post("/shows")
def post_show(show: schemas.Show, db: Session = Depends(get_db)) -> Any:
    show.last_updated = datetime.now()

    if show.id is None:
        add(show, models.Show, schemas.Show, redo_stack, db)
    else:
        update(show, models.Show, schemas.Show, redo_stack, db)

    redo_stack.clear()

@app.post("/movies")
def post_movie(movie: schemas.Movie, db: Session = Depends(get_db)) -> Any:
    movie.last_updated = datetime.now()

    if movie.id is None:
        add(movie, models.Movie, schemas.Movie, redo_stack, db)
    else:
        update(movie, models.Movie, schemas.Movie, redo_stack, db)

    redo_stack.clear()

@app.post("/webcomics")
def post_movie(webcomic: schemas.Webcomic, db: Session = Depends(get_db)) -> Any:
    webcomic.last_updated = datetime.now()

    if webcomic.id is None:
        add(webcomic, models.Webcomic, schemas.Webcomic, redo_stack, db)
    else:
        update(webcomic, models.Webcomic, schemas.Webcomic, redo_stack, db)

    redo_stack.clear()

@app.delete("/shows/{show_id}")
def delete_show(show_id: int, db: Session = Depends(get_db)) -> None:
    item = db.query(models.Show).get(show_id)
    delete(item, models.Show, schemas.Show, redo_stack, db)
    redo_stack.clear()

@app.delete("/movies/{movie_id}")

def delete_movie(movie_id: int, db: Session = Depends(get_db)) -> None:
    item = db.query(models.Movie).get(movie_id)
    delete(item, models.Movie, schemas.Movie, redo_stack, db)
    redo_stack.clear()

@app.delete("/webcomics/{webcomic_id}")
def delete_webcomic(webcomic_id: int, db: Session = Depends(get_db)) -> None:
    item = db.query(models.Webcomic).get(webcomic_id)
    delete(item, models.Webcomic, schemas.Webcomic, redo_stack, db)
    redo_stack.clear()

@app.post("/undo")
def undo(db: Session = Depends(get_db)) -> None:
    stack_operation(undo_stack, redo_stack, db)

@app.post("/redo")
def redo(db: Session = Depends(get_db)) -> None:
    stack_operation(redo_stack, undo_stack, db)

def add(obj: ModelTypes, model: Type[ModelTypes], schema: Type[SchemaTypes], reverse_stack: OperationStackType, db: Session) -> None:
    new_show = db.merge(model(**obj.dict()))
    db.flush()
    reverse_stack.append(("delete", model, schema, schema.from_orm(new_show)))
    db.commit()

def update(obj: ModelTypes, model: Type[ModelTypes], schema: Type[SchemaTypes], reverse_stack: OperationStackType, db: Session) -> None:
    item = schema.from_orm(db.query(model).get(obj.id))
    reverse_stack.append(("update", model, schema, item))
    db.merge(models.Show(**obj.dict()))
    db.commit()

def delete(obj: ModelTypes, model: Type[ModelTypes], schema: Type[SchemaTypes], reverse_stack: OperationStackType, db: Session) -> None:
    item = db.query(model).get(obj.id)
    reverse_stack.append(("add", model, schema, schema.from_orm(item)))
    db.delete(item)
    db.commit()

def stack_operation(stack: OperationStackType, reverse_stack: OperationStackType, db: Session) -> None:
    if not stack:
        return

    operation, model, schema, obj = stack.pop()

    if operation == "add":
        add(obj, model, schema, reverse_stack, db)
    elif operation == "update":
        update(obj, model, schema, reverse_stack, db)
    else:
        delete(obj, model, schema, reverse_stack, db)
