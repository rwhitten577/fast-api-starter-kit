from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DBBase(BaseModel):
    id: int
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    deleted: Optional[bool] = None

    class Config:
        orm_mode = True
