import re
from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime, event
from sqlalchemy.dialects import sqlite
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative, declared_attr

# Map Postgres UUID to sqlite VARCHAR for testing
CompatibleUUID = UUID(as_uuid=True).with_variant(sqlite.VARCHAR(), 'sqlite')


@as_declarative()
class Base:
    __name__: str

    # Generate __tablename__ automatically by converting CamelModelName to snake_model_name
    @declared_attr
    def __tablename__(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)
    modified = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted = Column(Boolean, nullable=False, default=False, server_default="false")

    __mapper_args__ = {"version_id_col": version}


# Callbacks for updates and inserts
def entity_update_listener(mapper, connection, target):
    target.modified = datetime.utcnow()


def entity_insert_listener(mapper, connection, target):
    target.create = datetime.utcnow()
    target.modified = target.created


event.listen(Base, 'before_update', entity_update_listener, propagate=True)
event.listen(Base, 'before_insert', entity_update_listener, propagate=True)


class User(Base):
    sub = Column(CompatibleUUID, unique=True, index=True, nullable=False)
    full_name = Column(String)
    given_name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    age = Column(Integer)
    gender = Column(Integer)
    timezone = Column(String)
    notifications_enabled = Column(Boolean(), default=True)
    email_enabled = Column(Boolean(), default=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
