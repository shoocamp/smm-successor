import pytest
from starlette.testclient import TestClient

from smm_successor.models.user import BaseUser
from smm_successor.server import app


@pytest.fixture(scope="session")
def authorized_client(request):
    client = TestClient(app)

    username = "test_user"
    password = "my_secret_password"
    email = "test_user@gmail.com"

    response = client.post('/api/v1/users/signup', data={
        'username': username,
        'password': password,
        'email': email,
    })

    client.headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    return client


@pytest.fixture(scope="session")
def current_user(authorized_client):
    response = authorized_client.get("/api/v1/users/info")
    return BaseUser(**response.json())
