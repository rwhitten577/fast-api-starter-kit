import re
from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime, event
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    __name__: str

    # Generate __tablename__ automatically by converting CamelModelName to snake_model_name
    @declared_attr
    def __tablename__(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

    version = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = Column(Boolean, nullable=False, default=False, server_default="0")

    __mapper_args__ = {"version_id_col": version}


# Callbacks for updates and inserts
def entity_update_listener(mapper, connection, target):
    target.modified = datetime.utcnow()


def entity_insert_listener(mapper, connection, target):
    target.created = datetime.utcnow()
    target.modified = target.created


event.listen(Base, 'before_update', entity_update_listener, propagate=True)
event.listen(Base, 'before_insert', entity_update_listener, propagate=True)


class User(Base):
    # id defined for each model so it can be used in queries.
    id = Column(Integer, primary_key=True)
    sub = Column(String(36), unique=True, index=True, nullable=False)
    full_name = Column(String(32))
    given_name = Column(String(32))
    email = Column(String(64), unique=True, index=True, nullable=False)
    age = Column(Integer)
    gender = Column(Integer)
    timezone = Column(String(32))
    notifications_enabled = Column(Boolean(), default=True)
    email_enabled = Column(Boolean(), default=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
