from typing import Type
import models
import schemas

ModelTypes = models.Show | models.Movie | models.Webcomic
SchemaTypes = schemas.Show | schemas.Movie | schemas.Webcomic
OperationStackType = list[tuple[str, Type[ModelTypes], Type[SchemaTypes], ModelTypes]]
