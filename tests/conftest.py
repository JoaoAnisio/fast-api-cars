import os

# Variáveis de ambiente de teste: definidas antes de importar o app, para os testes
# não dependerem do arquivo .env (o load_dotenv não sobrescreve variáveis já definidas).
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["MAX_DISCOUNT_SELLER"] = "10"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config import bcrypt_context
from dependencies import take_session
from main import app
from models import Base, User
from tests.data import CAR, CLIENT, PASSWORD

# Custo mínimo do bcrypt nos testes, para a suíte rodar rápido (em produção segue o padrão)
bcrypt_context.update(bcrypt__rounds=4)

@pytest.fixture()
def session_factory():
    # Banco SQLite em memória, isolado em cada teste (não toca no database.db)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine)
    engine.dispose()


@pytest.fixture()
def client(session_factory):
    def override_take_session():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[take_session] = override_take_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def make_user(client, session_factory):
    """Cria um usuário pela API, opcionalmente promove a admin e devolve (headers, user_id)."""
    def _make_user(email="seller@test.com", admin=False, active=True):
        response = client.post("/auth/create_user", json={"name": email, "email": email, "password": PASSWORD})
        assert response.status_code == 201
        with session_factory() as session:
            user = session.query(User).filter(User.email == email).first()
            user.admin = admin
            user.active = active
            session.commit()
            user_id = user.id
        token = client.post("/auth/login", json={"email": email, "password": PASSWORD})
        headers = {}
        if token.status_code == 200:
            headers = {"Authorization": f"Bearer {token.json()['access_token']}"}
        return headers, user_id
    return _make_user


@pytest.fixture()
def admin_headers(make_user):
    return make_user("admin@test.com", admin=True)[0]


@pytest.fixture()
def seller_headers(make_user):
    return make_user("seller@test.com")[0]


@pytest.fixture()
def other_seller_headers(make_user):
    return make_user("other@test.com")[0]


@pytest.fixture()
def create_car(client, admin_headers):
    counter = {"n": 0}

    def _create_car(price=50000.0):
        counter["n"] += 1
        payload = {**CAR, "model": f"Uno {counter['n']}", "price": price}
        response = client.post("/cars/add_car", json=payload, headers=admin_headers)
        assert response.status_code == 201
        return response.json()
    return _create_car


@pytest.fixture()
def create_client_record(client, admin_headers):
    def _create_client():
        response = client.post("/clients/add_client", json=CLIENT, headers=admin_headers)
        assert response.status_code == 201
        return response.json()
    return _create_client
