from fastapi.testclient import TestClient
from src.app.users.user_schema import Role
from src.tests.utils.utils import makeRequest, register_login_user, login_delete_user
from src.main import app
import pytest

client = TestClient(app)

username = "test1"
password = "password"

def test_create_product():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    r = makeRequest(
        client,
        "post",
        "products/",
        data={
            "title": "product",
            "price": 10,
            "description": "description",
            "quantity": 10
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["title"] == "product"
    assert r.json()["price"] == 10
    assert r.json()["description"] == "description"

def test_duplicate_product():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    r = makeRequest(
        client,
        "post",
        "products/",
        data={
            "title": "product",
            "price": 10,
            "description": "description",
            "quantity": 10
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200

    r = makeRequest(
        client,
        "post",
        "products/",
        data={
            "title": "product",
            "price": 10,
            "description": "description",
            "quantity": 10

        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 400
    assert "detail" in r.json()
    assert r.json()["detail"] == "Error while creating product"

def test_create_product_invalid_price():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    r = makeRequest(
        client,
        "post",
        "products/",
        data={
            "title": "product",
            "price": 3,
            "description": "description",
            "quantity": 10
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 400
    assert "detail" in r.json()
    assert r.json()["detail"] == "Invalid Denomination value. Allowed values are: 5, 10, 20, 50, 100"

def test_get_available_products():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None
    product = create_product("product2", 20, "description", 0, access_token)
    assert product is not None
    product = create_product("product3", 50, "description", 5, access_token)
    assert product is not None

    r = makeRequest(
        client,
        "get",
        "products/available-products",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert len(r.json()) == 2
    assert r.json()[0]["title"] == "product"
    assert r.json()[0]["price"] == 10
    assert r.json()[0]["description"] == "description"
    assert r.json()[0]["quantity"] == 10
    assert r.json()[1]["title"] == "product3"
    assert r.json()[1]["price"] == 50
    assert r.json()[1]["description"] == "description"
    assert r.json()[1]["quantity"] == 5
    
def test_get_product_details():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    r = makeRequest(
        client,
        "get",
        f"products/{product['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["title"] == "product"
    assert r.json()["price"] == 10
    assert r.json()["description"] == "description"
    assert r.json()["quantity"] == 10

def test_get_product_details_invalid_id():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    r = makeRequest(
        client,
        "get",
        f"products/100",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 404
    assert "detail" in r.json()
    assert r.json()["detail"] == "Product not found"

def test_update_product():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    r = makeRequest(
        client,
        "patch",
        f"products/{product['id']}",
        data={
            "title": "product2",
            "price": 20,
            "description": "description2",
            "quantity": 20
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["title"] == "product2"
    assert r.json()["price"] == 20
    assert r.json()["description"] == "description2"
    assert r.json()["quantity"] == 20

def test_update_product_invalid_id():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    r = makeRequest(
        client,
        "patch",
        f"products/100",
        data={
            "title": "product2",
            "price": 20,
            "description": "description2",
            "quantity": 20
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 404
    assert "detail" in r.json()
    assert r.json()["detail"] == "Product not found"

def test_update_product_invalid_owner():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    access_token = register_login_user(client, "test2", password, Role.seller.value)
    assert access_token is not None

    r = makeRequest(
        client,
        "patch",
        f"products/{product['id']}",
        data={
            "title": "product2",
            "price": 20,
            "description": "description2",
            "quantity": 20
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 404
    assert "detail" in r.json()
    assert r.json()["detail"] == "Product not found"
    login_delete_user(client, "test2", password)

def test_update_product_invalid_price():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    r = makeRequest(
        client,
        "patch",
        f"products/{product['id']}",
        data={
            "price": 3,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 400
    assert "detail" in r.json()
    assert r.json()["detail"] == "Invalid Denomination value. Allowed values are: 5, 10, 20, 50, 100"

def test_delete_product():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    r = makeRequest(
        client,
        "delete",
        f"products/{product['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert "message" in r.json()
    assert r.json()["message"] == "Product deleted"

def test_delete_product_invalid_id():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    r = makeRequest(
        client,
        "delete",
        f"products/100",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 404
    assert "detail" in r.json()
    assert r.json()["detail"] == "Product not found"

def test_delete_product_invalid_owner():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    access_token = register_login_user(client, "test2", password, Role.seller.value)
    assert access_token is not None

    r = makeRequest(
        client,
        "delete",
        f"products/{product['id']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 404
    assert "detail" in r.json()
    assert r.json()["detail"] == "Product not found"
    login_delete_user(client, "test2", password)

def test_buy_product():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    access_token = register_login_user(client, "test2", password, Role.buyer.value)
    assert access_token is not None

    r = makeRequest(
        client,
        "post",
        "users/deposit",
        data={"denomination": 50},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["balance"] == 50


    r = makeRequest(
        client,
        "get",
        f"products/buy/{product['id']}?quantity=1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()['username'] == "test2"
    assert r.json()['balance'] == 40
    assert len(r.json()['products']) == 1
    assert r.json()['products'][0]['title'] == "product"
    assert r.json()['products'][0]['price'] == 10
    assert r.json()['products'][0]['description'] == "description"
    assert r.json()['products'][0]['total_spent_on_product'] == 10
    assert r.json()['products'][0]['total_quantity_bought'] == 1
    login_delete_user(client, "test2", password)

def test_buy_product_invalid_id():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    access_token = register_login_user(client, "test2", password, Role.buyer.value)
    assert access_token is not None

    r = makeRequest(
        client,
        "post",
        "users/deposit",
        data={"denomination": 50},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["balance"] == 50


    r = makeRequest(
        client,
        "get",
        f"products/buy/100?quantity=1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 404
    assert "detail" in r.json()
    assert r.json()["detail"] == "Product not found or insufficient balance"
    login_delete_user(client, "test2", password)

def test_buy_product_invalid_quantity():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 10, "description", 10, access_token)
    assert product is not None

    access_token = register_login_user(client, "test2", password, Role.buyer.value)
    assert access_token is not None

    r = makeRequest(
        client,
        "post",
        "users/deposit",
        data={"denomination": 50},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["balance"] == 50


    r = makeRequest(
        client,
        "get",
        f"products/buy/{product['id']}?quantity=100",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 404
    assert "detail" in r.json()
    assert r.json()["detail"] == "Product not found or insufficient balance"
    login_delete_user(client, "test2", password)

def test_buy_product_insufficient_balance():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 20, "description", 10, access_token)
    assert product is not None

    access_token = register_login_user(client, "test2", password, Role.buyer.value)
    assert access_token is not None

    r = makeRequest(
        client,
        "post",
        "users/deposit",
        data={"denomination": 10},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["balance"] == 10


    r = makeRequest(
        client,
        "get",
        f"products/buy/{product['id']}?quantity=1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 404
    assert "detail" in r.json()
    assert r.json()["detail"] == "Product not found or insufficient balance"
    login_delete_user(client, "test2", password)

def test_partial_buy_product():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 20, "description", 10, access_token)
    assert product is not None

    access_token = register_login_user(client, "test2", password, Role.buyer.value)
    assert access_token is not None

    r = makeRequest(
        client,
        "post",
        "users/deposit",
        data={"denomination": 50},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["balance"] == 50


    r = makeRequest(
        client,
        "get",
        f"products/buy/{product['id']}?quantity=5",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 404
    assert "detail" in r.json()
    assert r.json()["detail"] == "Product not found or insufficient balance"
    login_delete_user(client, "test2", password)

def test_partial_buy_product_with_higher_balance():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product = create_product("product", 20, "description", 3, access_token)
    assert product is not None

    access_token = register_login_user(client, "test2", password, Role.buyer.value)
    assert access_token is not None

    r = makeRequest(
        client,
        "post",
        "users/deposit",
        data={"denomination": 100},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["balance"] == 100


    r = makeRequest(
        client,
        "get",
        f"products/buy/{product['id']}?quantity=5",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()['username'] == "test2"
    assert r.json()['balance'] == 40
    assert len(r.json()['products']) == 1
    assert r.json()['products'][0]['title'] == "product"
    assert r.json()['products'][0]['price'] == 20
    assert r.json()['products'][0]['description'] == "description"
    assert r.json()['products'][0]['total_spent_on_product'] == 60
    assert r.json()['products'][0]['total_quantity_bought'] == 3
    login_delete_user(client, "test2", password)

def test_buy_multiple_products():
    access_token = register_login_user(client, username, password, Role.seller.value)
    assert access_token is not None
    product1 = create_product("product1", 10, "description", 10, access_token)
    assert product1 is not None
    product2 = create_product("product2", 20, "description", 10, access_token)
    assert product2 is not None

    access_token = register_login_user(client, "test2", password, Role.buyer.value)
    assert access_token is not None

    r = makeRequest(
        client,
        "post",
        "users/deposit",
        data={"denomination": 100},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["balance"] == 100


    r = makeRequest(
        client,
        "get",
        f"products/buy/{product1['id']}?quantity=1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()['username'] == "test2"
    assert r.json()['balance'] == 90
    assert len(r.json()['products']) == 1
    assert r.json()['products'][0]['title'] == "product1"
    assert r.json()['products'][0]['price'] == 10
    assert r.json()['products'][0]['description'] == "description"
    assert r.json()['products'][0]['total_spent_on_product'] == 10
    assert r.json()['products'][0]['total_quantity_bought'] == 1

    r = makeRequest(
        client,
        "get",
        f"products/buy/{product2['id']}?quantity=1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()['username'] == "test2"
    assert r.json()['balance'] == 70
    assert len(r.json()['products']) == 2
    assert r.json()['products'][0]['title'] == "product1"
    assert r.json()['products'][0]['price'] == 10
    assert r.json()['products'][0]['description'] == "description"
    assert r.json()['products'][0]['total_spent_on_product'] == 10
    assert r.json()['products'][0]['total_quantity_bought'] == 1
    assert r.json()['products'][1]['title'] == "product2"
    assert r.json()['products'][1]['price'] == 20
    assert r.json()['products'][1]['description'] == "description"
    assert r.json()['products'][1]['total_spent_on_product'] == 20
    assert r.json()['products'][1]['total_quantity_bought'] == 1
    login_delete_user(client, "test2", password)


#Developer functions
def create_product(title, price, description, quantity, access_token):
    r = makeRequest(
        client,
        "post",
        "products/",
        data={
            "title": title,
            "price": price,
            "quantity": quantity,
            "description": description,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return r.json()


@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir):
    yield
    login_delete_user(client, username, password)
