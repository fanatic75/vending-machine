from fastapi.testclient import TestClient
from src.app.users.user_schema import Role
from src.core.config import settings


def makeRequest(
    client: TestClient, method: str, url: str, headers: dict = {}, data: dict = {}
):
    return client.request(
        method, f"{settings.API_V1_STR}/{url}", headers=headers, json=data
    )


def register_login_user(
    client: TestClient, username: str, password: str, role=Role.buyer.value
):
    r = makeRequest(
        client,
        "post",
        "users/",
        data={"username": username, "password": password, "role": role},
    )

    if r.status_code == 400:
        return None

    r = makeRequest(
        client,
        "post",
        "users/login",
        data={"username": username, "password": password},
    )

    if r.status_code == 404:
        return None

    access_token: str = r.json()["access_token"]
    return access_token


def login_delete_user(client: TestClient, username: str, password: str):
    r = makeRequest(
        client,
        "post",
        "users/login",
        data={"username": username, "password": password},
    )

    if r.status_code == 404:
        return
    access_token = r.json()["access_token"]

    r = makeRequest(
        client, "delete", "users/", headers={"Authorization": f"Bearer {access_token}"}
    )
