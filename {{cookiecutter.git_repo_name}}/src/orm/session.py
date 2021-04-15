import sys

import pymysql.converters
import pendulum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core import settings

# Set converter for Pendulum date type.
pymysql.converters.conversions[pendulum.DateTime] = pymysql.converters.escape_datetime

db_url = "sqlite://" if "pytest" in sys.modules else settings.database_url
engine = create_engine(db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
