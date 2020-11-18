from typing import Generator

import requests
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.JWTBearer import JWKS, JWTBearer, JWTAuthorizationCredentials
from src.core.settings import settings
from src.orm.models import User
from src.orm.session import SessionLocal
from src.services.crud.user_crud import UserCrud

jwks = JWKS.parse_obj(
    requests.get(
        f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/"
        f"{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    ).json()
)


auth = JWTBearer(jwks)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(db: Session = Depends(get_db), credentials: JWTAuthorizationCredentials = Depends(auth)) -> User:
    try:
        sub = credentials.claims["sub"]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = UserCrud(db).get_by_sub(sub=sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The user doesn't have enough privileges"
        )
    return current_user
