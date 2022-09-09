from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status, Header, Response
from sqlalchemy.orm import Session
from typing import Any, Iterator, Type
import database
import models
import schemas

ModelTypes = models.Show | models.Movie | models.Webcomic
SchemaTypes = schemas.Show | schemas.Movie | schemas.Webcomic
OperationStackType = list[tuple[str, Type[ModelTypes], Type[SchemaTypes], SchemaTypes]]

app = FastAPI(debug=True)
database.Base.metadata.create_all(database.engine)

undo_stack: OperationStackType = []
redo_stack: OperationStackType = []

last_fetch_time: datetime = datetime.now()

def get_db() -> Iterator[Session]:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/shows", response_model=list[schemas.Show])
def get_shows(response: Response, db: Session = Depends(get_db)) -> Any:
    global last_fetch_time
    last_fetch_time = datetime.now()
    response.headers["Fetch-Time"] = last_fetch_time.isoformat()
    return db.query(models.Show).all()

@app.get("/movies", response_model=list[schemas.Movie])
def get_movies(response: Response, db: Session = Depends(get_db)) -> Any:
    global last_fetch_time
    last_fetch_time = datetime.now()
    response.headers["Fetch-Time"] = last_fetch_time.isoformat()
    return db.query(models.Movie).all()

@app.get("/webcomics", response_model=list[schemas.Webcomic])
def get_webcomics(response: Response, db: Session = Depends(get_db)) -> Any:
    global last_fetch_time
    last_fetch_time = datetime.now()
    response.headers["Fetch-Time"] = last_fetch_time.isoformat()
    return db.query(models.Webcomic).all()

@app.post("/shows", status_code=status.HTTP_204_NO_CONTENT)
def post_show(show: schemas.Show, fetch_time: datetime = Header(default=None), db: Session = Depends(get_db)) -> Any:
    if fetch_time is not None and fetch_time != last_fetch_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fetch time out of date.")

    show.last_updated = datetime.now()

    if show.id is None:
        add(show, models.Show, schemas.Show, undo_stack, db)
    else:
        update(show, models.Show, schemas.Show, undo_stack, db)

    redo_stack.clear()

@app.post("/movies", status_code=status.HTTP_204_NO_CONTENT)
def post_movie(movie: schemas.Movie, fetch_time: datetime = Header(default=None), db: Session = Depends(get_db)) -> Any:
    if fetch_time is not None and fetch_time != last_fetch_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fetch time out of date.")

    movie.last_updated = datetime.now()

    if movie.id is None:
        add(movie, models.Movie, schemas.Movie, undo_stack, db)
    else:
        update(movie, models.Movie, schemas.Movie, undo_stack, db)

    redo_stack.clear()

@app.post("/webcomics", status_code=status.HTTP_204_NO_CONTENT)
def post_webcomic(webcomic: schemas.Webcomic, fetch_time: datetime = Header(default=None), db: Session = Depends(get_db)) -> Any:
    if fetch_time is not None and fetch_time != last_fetch_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fetch time out of date.")

    webcomic.last_updated = datetime.now()

    if webcomic.id is None:
        add(webcomic, models.Webcomic, schemas.Webcomic, undo_stack, db)
    else:
        update(webcomic, models.Webcomic, schemas.Webcomic, undo_stack, db)

    redo_stack.clear()

@app.delete("/shows/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_show(show_id: int, fetch_time: datetime = Header(default=None), db: Session = Depends(get_db)) -> None:
    if fetch_time is not None and fetch_time != last_fetch_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fetch time out of date.")

    item = schemas.Show()
    item.id = show_id
    delete(item, models.Show, schemas.Show, undo_stack, db)
    redo_stack.clear()

@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, fetch_time: datetime = Header(default=None), db: Session = Depends(get_db)) -> None:
    if fetch_time is not None and fetch_time != last_fetch_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fetch time out of date.")

    item = schemas.Movie()
    item.id = movie_id
    delete(item, models.Movie, schemas.Movie, undo_stack, db)
    redo_stack.clear()

@app.delete("/webcomics/{webcomic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webcomic(webcomic_id: int, fetch_time: datetime = Header(default=None), db: Session = Depends(get_db)) -> None:
    if fetch_time is not None and fetch_time != last_fetch_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fetch time out of date.")

    item = schemas.Webcomic()
    item.id = webcomic_id
    delete(item, models.Webcomic, schemas.Webcomic, undo_stack, db)
    redo_stack.clear()

@app.post("/undo", status_code=status.HTTP_204_NO_CONTENT)
def undo(fetch_time: datetime = Header(default=None), db: Session = Depends(get_db)) -> None:
    if fetch_time is not None and fetch_time != last_fetch_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fetch time out of date.")

    stack_operation(undo_stack, redo_stack, db)

@app.post("/redo", status_code=status.HTTP_204_NO_CONTENT)
def redo(fetch_time: datetime = Header(default=None), db: Session = Depends(get_db)) -> None:
    if fetch_time is not None and fetch_time != last_fetch_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fetch time out of date.")

    stack_operation(redo_stack, undo_stack, db)

def add(obj: SchemaTypes, model: Type[ModelTypes], schema: Type[SchemaTypes], stack: OperationStackType, db: Session) -> None:
    new_show = db.merge(model(**obj.dict()))
    db.flush()
    stack.append(("delete", model, schema, schema.from_orm(new_show)))
    db.commit()

def update(obj: SchemaTypes, model: Type[ModelTypes], schema: Type[SchemaTypes], stack: OperationStackType, db: Session) -> None:
    item = db.query(model).get(obj.id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, detail="No entry with corresponding id.")
    stack.append(("update", model, schema, schema.from_orm(item)))
    db.merge(model(**obj.dict()))
    db.commit()

def delete(obj: SchemaTypes, model: Type[ModelTypes], schema: Type[SchemaTypes], stack: OperationStackType, db: Session) -> None:
    item = db.query(model).get(obj.id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, detail="No entry with corresponding id.")
    stack.append(("add", model, schema, schema.from_orm(item)))
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
