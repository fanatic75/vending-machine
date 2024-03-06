from fastapi.testclient import TestClient
from src.app.users.user_schema import Role
from src.tests.utils.utils import makeRequest, login_delete_user, register_login_user, generate_random_word
from src.main import app
import pytest

client = TestClient(app)

username = generate_random_word(10)
password = "password"


def test_register_user():

    r = makeRequest(
        client,
        "post",
        "users/",
        data={"username": username, "password": password, "role": Role.buyer.value},
    )

    assert r.status_code == 200
    assert r.json()["username"] == username
    assert r.json()["role"] == Role.buyer.value
    assert "id" in r.json()
    assert r.json()["products"] == []
    assert r.json()["balance"] == 0


def test_register_user_existing_username():

    r = makeRequest(
        client,
        "post",
        "users/",
        data={"username": username, "password": password, "role": Role.buyer.value},
    )

    assert r.status_code == 200

    r = makeRequest(
        client,
        "post",
        "users/",
        data={"username": username, "password": password, "role": Role.buyer.value},
    )

    assert r.status_code == 400
    assert "detail" in r.json()
    assert (
        r.json()["detail"]
        == "The user with this username already exists in the system."
    )


def test_register_user_invalid_role():

    r = makeRequest(
        client,
        "post",
        "users/",
        data={"username": username, "password": password, "role": "invalid"},
    )

    assert r.status_code == 422
    assert "detail" in r.json()
    assert r.json()["detail"][0]["msg"] == "Input should be 'buyer' or 'seller'"

    r = makeRequest(
        client,
        "post",
        "users/",
        data={"username": username, "password": password, "role": Role.buyer.value},
    )

    assert r.status_code == 200
    assert r.json()["role"] == Role.buyer.value


def test_invalid_login_details():

    r = makeRequest(
        client,
        "post",
        "users/",
        data={"username": username, "password": password, "role": Role.buyer.value},
    )

    assert r.status_code == 200

    r = makeRequest(
        client,
        "post",
        "users/login",
        data={"username": username, "password": "invalid"},
    )

    assert r.status_code == 404
    assert "detail" in r.json()
    assert r.json()["detail"] == "Invalid username or password"


def test_login_get_details():

    access_token = register_login_user(client, username, password)
    assert access_token is not None

    r = makeRequest(
        client, "get", "users/", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert r.status_code == 200
    assert r.json()["username"] == username
    assert r.json()["role"] == Role.buyer.value
    assert "id" in r.json()
    assert r.json()["products"] == []
    assert r.json()["balance"] == 0


def test_login_update_user():
    access_token = register_login_user(client,username, password)
    assert access_token is not None

    new_username = generate_random_word(10)
    new_password = "new_password"

    r = makeRequest(
        client,
        "patch",
        "users/",
        data={"new_username": new_username, "new_password": new_password},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["username"] == new_username
    assert r.json()["role"] == Role.buyer.value
    assert "id" in r.json()
    assert r.json()["products"] == []
    assert r.json()["balance"] == 0
    login_delete_user(client, new_username, new_password)


def test_deposit_amount():
    access_token = register_login_user(client, username, password)
    assert access_token is not None
    amount = 100

    r = makeRequest(
        client,
        "post",
        "users/deposit",
        data={"denomination": amount},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["username"] == username
    assert r.json()["role"] == Role.buyer.value
    assert "id" in r.json()
    assert r.json()["products"] == []
    assert r.json()["balance"] == amount

def test_invalid_deposit_amount():
    access_token = register_login_user(client, username, password)
    assert access_token is not None
    amount = 101

    r = makeRequest(
        client,
        "post",
        "users/deposit",
        data={"denomination": amount},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 400
    assert "detail" in r.json()
    assert r.json()["detail"] == "Invalid Denomination value. Allowed values are: 5, 10, 20, 50, 100"

def test_reset_amount():
    access_token = register_login_user(client, username, password)
    assert access_token is not None
    amount = 100

    r = makeRequest(
        client,
        "post",
        "users/deposit",
        data={"denomination": amount},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["username"] == username
    assert r.json()["role"] == Role.buyer.value
    assert "id" in r.json()
    assert r.json()["products"] == []
    assert r.json()["balance"] == amount

    r = makeRequest(
        client,
        "post",
        "users/reset",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert r.status_code == 200
    assert r.json()["username"] == username
    assert r.json()["role"] == Role.buyer.value
    assert "id" in r.json()
    assert r.json()["products"] == []
    assert r.json()["balance"] == 0



@pytest.fixture(autouse=True)
def run_before_and_after_tests(tmpdir):
    yield
    login_delete_user(client, username, password)
