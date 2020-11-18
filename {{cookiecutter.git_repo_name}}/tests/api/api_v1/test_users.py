from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from src.orm.models import User


def test_create_user(db_session, client, user_sub):
    user = db_session.query(User).one_or_none()
    assert not user

    user_data = {
        "sub": user_sub,
        "full_name": "Joe Test",
        "given_name": "Joe",
        "email": "joe.test@email.com",
        "timezone": "America/New_York"
    }

    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200

    user = db_session.query(User).one_or_none()

    assert response.json() == {
        'full_name': 'Joe Test',
        'given_name': 'Joe',
        'email': 'joe.test@email.com',
        'age': None,
        'gender': None,
        'timezone': "America/New_York",
        'notifications_enabled': True,
        'email_enabled': True,
        'is_active': True,
        'is_superuser': False,
        'id': user.id,
        'sub': user_sub,
        'created': jsonable_encoder(user.created),
        'modified': jsonable_encoder(user.modified),
        'deleted': False,
    }

    user = db_session.query(User).one_or_none()
    assert user


def test_create_user_sub_doesnt_match_token(db_session, client):
    user = db_session.query(User).one_or_none()
    assert not user

    user_data = {
        "sub": "not-a-real-sub",
        "full_name": "Joe Test",
        "given_name": "Joe",
        "email": "joe.test@email.com",
        "timezone": "America/New_York"
    }

    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400


def test_create_user_already_exists(db_session, client, user_sub):
    user = User(sub=user_sub, email="test@email.com", full_name="test user", given_name="test")
    db_session.add(user)
    db_session.commit()

    user_data = {
        "sub": user_sub,
        "full_name": "Joe Test",
        "given_name": "Joe",
        "email": "joe.test@email.com",
        "timezone": "America/New_York",
    }

    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400


def test_read_users(db_session, client, user_sub):
    user = User(sub=user_sub, email="test@email.com", full_name="test user", given_name="test", is_superuser=False)
    db_session.add(user)
    db_session.commit()

    response = client.get("/api/v1/users/")
    assert response.status_code == 400

    user.is_superuser = True
    db_session.commit()

    response = client.get("/api/v1/users/")
    assert response.status_code == 200

    json_resp = response.json()
    assert isinstance(json_resp, list)
    assert len(json_resp) == 1
    assert json_resp[0]["sub"] == user_sub


def test_update_user(db_session, client, user_sub):
    user = User(sub=user_sub, email="test@email.com", full_name="test user", given_name="test",
                is_superuser=False)
    db_session.add(user)
    db_session.commit()

    # Sub cannot be set, assert it is unchanged
    user_data = {
        "sub": "new-sub",
        "full_name": "Joe Test",
        "given_name": "Joe",
        "email": "joe.test@email.com",
        "age": 25,
        "gender": 0,
    }

    response = client.patch("/api/v1/users/me", json=user_data)
    assert response.status_code == 200

    updated_user = response.json()
    assert updated_user.get("sub") == user_sub
    assert updated_user.get("age") == user_data["age"]

    # Cannot set self to superuser
    user_data = {
        "is_superuser": True
    }

    response = client.patch("/api/v1/users/me", json=user_data)
    assert response.status_code == 400


def test_read_user_me(db_session, client, user_sub):
    user = User(sub=user_sub, email="test@email.com", full_name="test user", given_name="test",
                is_superuser=False)
    db_session.add(user)
    db_session.commit()

    response = client.get("/api/v1/users/me")
    assert response.status_code == 200
    assert response.json().get("sub") == user.sub
    assert response.json().get("email") == user.email


def test_read_user_by_id(db_session, client, user_sub):
    user = User(sub=user_sub, email="test@email.com", full_name="test user", given_name="test",
                is_superuser=False)
    db_session.add(user)
    db_session.commit()

    response = client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200

    user_2 = User(sub=str(uuid4()), email="test2@email.com", full_name="test user 2", given_name="test 2",
                  is_superuser=False)
    db_session.add(user_2)
    db_session.commit()

    response = client.get(f"/api/v1/users/{user_2.id}")
    assert response.status_code == 400

    user.is_superuser = True
    db_session.add(user)
    db_session.commit()

    response = client.get(f"/api/v1/users/{user_2.id}")
    assert response.status_code == 200
    assert response.json().get("email") == user_2.email


def test_update_user_by_id(db_session, client, user_sub):
    user = User(sub=user_sub, email="test@email.com", full_name="test user", given_name="test",
                is_superuser=False)
    db_session.add(user)

    user_2 = User(sub=str(uuid4()), email="test2@email.com", full_name="test user 2",
                  given_name="test 2",
                  is_superuser=False)
    db_session.add(user_2)
    db_session.commit()

    update_data = {
        "is_active": False
    }

    response = client.patch(f"/api/v1/users/{user_2.id}", json=update_data)
    assert response.status_code == 400

    user.is_superuser = True
    db_session.add(user)
    db_session.commit()

    response = client.patch("/api/v1/users/5", json=update_data)
    assert response.status_code == 404

    response = client.patch(f"/api/v1/users/{user_2.id}", json=update_data)
    assert response.status_code == 200

    assert not user_2.is_active
