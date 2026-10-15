import pytest


@pytest.fixture()
def order_data(create_car, create_client_record):
    return {"car": create_car(price=100000.0), "client": create_client_record()}


def new_order(client, headers, car_id, client_id, discount=0):
    return client.post(
        "/orders/create_order",
        json={"car_id": car_id, "client_id": client_id, "discount": discount},
        headers=headers,
    )


def test_create_order_calculates_total_price(client, seller_headers, order_data):
    response = new_order(client, seller_headers, order_data["car"]["id"], order_data["client"]["id"], discount=10)
    assert response.status_code == 201
    order = client.get(f"/orders/get_order/{response.json()['order_id']}", headers=seller_headers).json()
    assert order["car_price"] == 100000.0
    assert order["discount"] == 10
    assert order["total_price"] == pytest.approx(90000.0)
    assert order["status"] == "PENDING"


def test_create_order_requires_authentication(client, order_data):
    response = client.post("/orders/create_order", json={"car_id": 1, "client_id": 1})
    assert response.status_code == 401


def test_create_order_car_or_client_not_found(client, seller_headers, order_data):
    assert new_order(client, seller_headers, 999, order_data["client"]["id"]).status_code == 404
    assert new_order(client, seller_headers, order_data["car"]["id"], 999).status_code == 404


def test_car_cannot_have_two_active_orders(client, seller_headers, order_data):
    car_id, client_id = order_data["car"]["id"], order_data["client"]["id"]
    assert new_order(client, seller_headers, car_id, client_id).status_code == 201
    assert new_order(client, seller_headers, car_id, client_id).status_code == 409


def test_canceled_order_frees_the_car(client, seller_headers, order_data):
    car_id, client_id = order_data["car"]["id"], order_data["client"]["id"]
    order_id = new_order(client, seller_headers, car_id, client_id).json()["order_id"]
    assert client.post(f"/orders/order/cancel/{order_id}", headers=seller_headers).status_code == 200
    assert new_order(client, seller_headers, car_id, client_id).status_code == 201


def test_order_is_registered_for_the_token_user(client, make_user, order_data):
    seller_headers, seller_id = make_user("seller@test.com")
    new_order(client, seller_headers, order_data["car"]["id"], order_data["client"]["id"])
    orders = client.get("/orders/my_orders", headers=seller_headers).json()
    assert len(orders) == 1


@pytest.mark.parametrize("discount, expected_status", [(0, 201), (10, 201), (10.01, 403), (50, 403), (100, 403)])
def test_seller_discount_limit(client, seller_headers, order_data, discount, expected_status):
    response = new_order(client, seller_headers, order_data["car"]["id"], order_data["client"]["id"], discount)
    assert response.status_code == expected_status


def test_admin_can_exceed_seller_discount_limit(client, admin_headers, order_data):
    response = new_order(client, admin_headers, order_data["car"]["id"], order_data["client"]["id"], discount=50)
    assert response.status_code == 201


@pytest.mark.parametrize("discount", [-1, 100.5, 150])
def test_discount_outside_0_100_is_invalid(client, admin_headers, order_data, discount):
    response = new_order(client, admin_headers, order_data["car"]["id"], order_data["client"]["id"], discount)
    assert response.status_code == 422


def test_my_orders_returns_only_own_orders(client, seller_headers, other_seller_headers, create_car, create_client_record):
    client_id = create_client_record()["id"]
    new_order(client, seller_headers, create_car()["id"], client_id)
    new_order(client, other_seller_headers, create_car()["id"], client_id)
    assert len(client.get("/orders/my_orders", headers=seller_headers).json()) == 1
    assert len(client.get("/orders/my_orders", headers=other_seller_headers).json()) == 1


def test_list_orders_is_admin_only(client, seller_headers, admin_headers, order_data):
    new_order(client, seller_headers, order_data["car"]["id"], order_data["client"]["id"])
    assert client.get("/orders/list_orders", headers=seller_headers).status_code == 403
    response = client.get("/orders/list_orders", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_seller_cannot_access_someone_elses_order(client, seller_headers, other_seller_headers, order_data):
    order_id = new_order(client, seller_headers, order_data["car"]["id"], order_data["client"]["id"]).json()["order_id"]
    assert client.get(f"/orders/get_order/{order_id}", headers=other_seller_headers).status_code == 403
    assert client.post(f"/orders/order/cancel/{order_id}", headers=other_seller_headers).status_code == 403
    assert client.post(f"/orders/order/complete/{order_id}", headers=other_seller_headers).status_code == 403
    assert client.delete(f"/orders/delete_order/{order_id}", headers=other_seller_headers).status_code == 403


def test_admin_can_access_any_order(client, seller_headers, admin_headers, order_data):
    order_id = new_order(client, seller_headers, order_data["car"]["id"], order_data["client"]["id"]).json()["order_id"]
    assert client.get(f"/orders/get_order/{order_id}", headers=admin_headers).status_code == 200
    assert client.post(f"/orders/order/cancel/{order_id}", headers=admin_headers).status_code == 200


def test_get_order_not_found(client, seller_headers):
    assert client.get("/orders/get_order/999", headers=seller_headers).status_code == 404


def test_complete_order(client, seller_headers, order_data):
    order_id = new_order(client, seller_headers, order_data["car"]["id"], order_data["client"]["id"]).json()["order_id"]
    response = client.post(f"/orders/order/complete/{order_id}", headers=seller_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_only_pending_orders_can_change_status(client, seller_headers, order_data):
    order_id = new_order(client, seller_headers, order_data["car"]["id"], order_data["client"]["id"]).json()["order_id"]
    client.post(f"/orders/order/complete/{order_id}", headers=seller_headers)
    assert client.post(f"/orders/order/cancel/{order_id}", headers=seller_headers).status_code == 400
    assert client.post(f"/orders/order/complete/{order_id}", headers=seller_headers).status_code == 400


def test_delete_order(client, seller_headers, order_data):
    order_id = new_order(client, seller_headers, order_data["car"]["id"], order_data["client"]["id"]).json()["order_id"]
    assert client.delete(f"/orders/delete_order/{order_id}", headers=seller_headers).status_code == 200
    assert client.get(f"/orders/get_order/{order_id}", headers=seller_headers).status_code == 404
