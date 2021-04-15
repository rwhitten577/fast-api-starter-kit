from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from src.api import deps
from src.api.JWTBearer import JWTAuthorizationCredentials
from src.orm import models, schemas
from src.services.crud.user_crud import UserCrud

router = APIRouter()


@router.get("/", response_model=List[schemas.User], dependencies=[Depends(
    deps.get_current_active_superuser)])
def read_users(db: Session = Depends(deps.get_db), offset: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    users = UserCrud(db).get_multi(offset=offset, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(*, db: Session = Depends(deps.get_db), user_in: schemas.UserCreate,
                credentials: JWTAuthorizationCredentials = Depends(deps.auth)) -> Any:
    """
    Create new user.
    """
    crud = UserCrud(db)
    user = crud.get_by_sub(sub=user_in.sub)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this username already exists in the system.",
        )
    if not credentials.claims.get("sub") == user_in.sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credentials do not match input data.",
        )
    user = crud.create(obj_in=user_in)
    return user


@router.patch("/me", response_model=schemas.User)
def update_user_me(*, db: Session = Depends(deps.get_db), user_in: schemas.UserUpdate,
                   current_user: models.User = Depends(deps.get_current_active_user)) -> Any:
    """
    Update own user.
    """
    if not current_user.is_superuser and user_in.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot set self to superuser.",
        )

    current_user_data = jsonable_encoder(current_user)
    user_update = schemas.UserUpdate(**current_user_data)
    update_data = user_in.dict(exclude_unset=True)
    updated_user = user_update.copy(update=update_data)
    user = UserCrud(db).update(db_obj=current_user, obj_in=updated_user)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(current_user: models.User = Depends(deps.get_current_active_user)) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(user_id: int, current_user: models.User = Depends(deps.get_current_active_user),
                    db: Session = Depends(deps.get_db)) -> Any:
    """
    Get a specific user by id.
    """
    crud = UserCrud(db)
    user = crud.get(id=user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The user doesn't have enough privileges"
        )
    return user


@router.patch("/{user_id}", response_model=schemas.User, dependencies=[Depends(deps.get_current_active_superuser)])
def update_user(*, db: Session = Depends(deps.get_db), user_id: int, user_in: schemas.UserUpdate) -> Any:
    """
    Update a user. To be used by superusers only, e.g. set user as inactive.
    """
    crud = UserCrud(db)
    user = crud.get(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    current_user_data = jsonable_encoder(user)
    user_update = schemas.UserUpdate(**current_user_data)
    update_data = user_in.dict(exclude_unset=True)
    updated_user = user_update.copy(update=update_data)
    user = crud.update(db_obj=user, obj_in=updated_user)
    return user
