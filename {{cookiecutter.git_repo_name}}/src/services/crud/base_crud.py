from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.orm.models import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseCrud(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        return self.db.query(self.model) \
            .filter(self.model.id == id) \
            .filter(self.model.deleted == False).first()

    def get_with_deleted(self, id: Any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, *, offset: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model) \
            .filter(self.model.deleted == False) \
            .order_by(self.model.created.asc()) \
            .offset(offset).limit(limit).all()

    def create(self, *, obj_in: CreateSchemaType, commit: bool = True) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        self.db.add(db_obj)
        self.db.commit()
        return db_obj

    def update(self, *, db_obj: ModelType,
               obj_in: Union[UpdateSchemaType, Dict[str, Any]],
               commit: bool = True) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        self.db.add(db_obj)

        if commit:
            self.db.commit()

        return db_obj

    def remove(self, *, id: int) -> ModelType:
        obj = self.db.query(self.model).get(id)
        obj.deleted = True
        self.db.commit()
        return obj
