from tests.data import CAR, CLIENT


def test_add_car_requires_admin(client, seller_headers):
    response = client.post("/cars/add_car", json=CAR, headers=seller_headers)
    assert response.status_code == 403


def test_admin_adds_car(client, admin_headers):
    response = client.post("/cars/add_car", json=CAR, headers=admin_headers)
    assert response.status_code == 201
    assert response.json()["id"] > 0
    assert response.json()["model"] == CAR["model"]


def test_add_car_invalid_payload(client, admin_headers):
    response = client.post("/cars/add_car", json={"make": "Fiat"}, headers=admin_headers)
    assert response.status_code == 422


def test_list_and_get_car(client, seller_headers, create_car):
    car = create_car()
    listed = client.get("/cars/list_cars", headers=seller_headers)
    assert listed.status_code == 200
    assert [c["id"] for c in listed.json()] == [car["id"]]
    assert client.get(f"/cars/get_car/{car['id']}", headers=seller_headers).json()["id"] == car["id"]


def test_get_car_not_found(client, seller_headers):
    assert client.get("/cars/get_car/999", headers=seller_headers).status_code == 404


def test_add_list_and_get_client(client, seller_headers):
    created = client.post("/clients/add_client", json=CLIENT, headers=seller_headers)
    assert created.status_code == 201
    client_id = created.json()["id"]
    assert client.get("/clients/list_clients", headers=seller_headers).json()[0]["id"] == client_id
    assert client.get(f"/clients/get_client/{client_id}", headers=seller_headers).json()["email"] == CLIENT["email"]


def test_get_client_not_found(client, seller_headers):
    assert client.get("/clients/get_client/999", headers=seller_headers).status_code == 404


def test_add_client_duplicated_document_or_email(client, seller_headers):
    assert client.post("/clients/add_client", json=CLIENT, headers=seller_headers).status_code == 201
    same_document = {**CLIENT, "email": "outro@test.com"}
    same_email = {**CLIENT, "document": "999.999.999-99"}
    assert client.post("/clients/add_client", json=same_document, headers=seller_headers).status_code == 409
    assert client.post("/clients/add_client", json=same_email, headers=seller_headers).status_code == 409


def test_clients_and_cars_require_authentication(client):
    assert client.get("/clients/list_clients").status_code == 401
    assert client.post("/cars/add_car", json=CAR).status_code == 401
