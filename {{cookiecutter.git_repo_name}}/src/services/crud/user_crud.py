from typing import Optional

from sqlalchemy.orm import Session

from src.services.crud.base_crud import BaseCrud
from src.orm.models import User
from src.orm.schemas import UserCreate, UserUpdate


class UserCrud(BaseCrud[User, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        super(UserCrud, self).__init__(User, db)

    def get_by_sub(self, *, sub: str) -> Optional[User]:
        return self.db.query(self.model).filter(User.sub == sub).first()
