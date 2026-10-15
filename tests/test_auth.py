from jose import jwt

from config import ALGORITHM, SECRET_KEY, bcrypt_context
from models import User
from tests.data import PASSWORD

NEW_USER = {"name": "Joana", "email": "joana@test.com", "password": PASSWORD}


def login(client, email="joana@test.com", password=PASSWORD):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_create_user(client):
    response = client.post("/auth/create_user", json=NEW_USER)
    assert response.status_code == 201


def test_create_user_duplicated_email(client):
    client.post("/auth/create_user", json=NEW_USER)
    response = client.post("/auth/create_user", json=NEW_USER)
    assert response.status_code == 409


def test_password_is_stored_hashed(client, session_factory):
    client.post("/auth/create_user", json=NEW_USER)
    with session_factory() as session:
        user = session.query(User).filter(User.email == NEW_USER["email"]).first()
        assert user.password != PASSWORD
        assert bcrypt_context.verify(PASSWORD, user.password)


def test_signup_cannot_create_admin(client, session_factory):
    payload = {**NEW_USER, "admin": True, "active": False}
    assert client.post("/auth/create_user", json=payload).status_code == 201
    with session_factory() as session:
        user = session.query(User).filter(User.email == NEW_USER["email"]).first()
        assert user.admin is False
        assert user.active is True


def test_login_returns_access_and_refresh_tokens(client):
    client.post("/auth/create_user", json=NEW_USER)
    response = login(client)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert jwt.decode(body["access_token"], SECRET_KEY, algorithms=[ALGORITHM])["type"] == "access"
    assert jwt.decode(body["refresh_token"], SECRET_KEY, algorithms=[ALGORITHM])["type"] == "refresh"


def test_login_wrong_password(client):
    client.post("/auth/create_user", json=NEW_USER)
    assert login(client, password="errada123").status_code == 401


def test_login_unknown_email_has_same_error_as_wrong_password(client):
    client.post("/auth/create_user", json=NEW_USER)
    wrong_password = login(client, password="errada123")
    unknown_email = login(client, email="naoexiste@test.com")
    assert unknown_email.status_code == wrong_password.status_code == 401
    assert unknown_email.json() == wrong_password.json()


def test_login_inactive_user(make_user):
    headers, _ = make_user("inativo@test.com", active=False)
    assert headers == {}


def test_login_form_for_swagger(client):
    client.post("/auth/create_user", json=NEW_USER)
    response = client.post("/auth/login-form", data={"username": NEW_USER["email"], "password": PASSWORD})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_token_with_refresh_token(client):
    client.post("/auth/create_user", json=NEW_USER)
    refresh = login(client).json()["refresh_token"]
    response = client.get("/auth/refresh_token", headers={"Authorization": f"Bearer {refresh}"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_endpoint_rejects_access_token(client):
    client.post("/auth/create_user", json=NEW_USER)
    access = login(client).json()["access_token"]
    response = client.get("/auth/refresh_token", headers={"Authorization": f"Bearer {access}"})
    assert response.status_code == 401


def test_protected_route_rejects_refresh_token(client):
    client.post("/auth/create_user", json=NEW_USER)
    refresh = login(client).json()["refresh_token"]
    response = client.get("/cars/list_cars", headers={"Authorization": f"Bearer {refresh}"})
    assert response.status_code == 401


def test_protected_route_without_token(client):
    assert client.get("/cars/list_cars").status_code == 401


def test_protected_route_with_invalid_token(client):
    response = client.get("/cars/list_cars", headers={"Authorization": "Bearer abc.def.ghi"})
    assert response.status_code == 401


def test_token_of_deactivated_user_is_rejected(make_user, client, session_factory):
    headers, user_id = make_user("vai-sair@test.com")
    with session_factory() as session:
        session.query(User).filter(User.id == user_id).first().active = False
        session.commit()
    assert client.get("/cars/list_cars", headers=headers).status_code == 403
