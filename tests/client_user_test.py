from fastapi.testclient import TestClient
from app.core.config import settings
from fastapi import status
from app.models.model import User, Token
from sqlalchemy.orm import Session
from tests.main import url_client, client_create,url_login

def test_create_user(client: TestClient, db: Session):
    response = client.post(
        url_client,
        json={"email": "testuser@example.com", "password": "testpassword"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

def test_login_user(client: TestClient, db: Session):
    # First, create a user
    client.post(
        url_client,
        json={"email": "testuser@example.com", "password": "testpassword"}
    )
    # Then, login with the created user
    response = client.post(
        url_login,
        data={"username": "testuser@example.com", "password": "testpassword"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_user(client: TestClient, db: Session):
    # First, create a user
    response = client.post(
        url_client,
        json={"email": "testuser@example.com", "password": "testpassword"}
    )
    user_id = response.json()["id"]
    # Then, get the created user
    response = client.get(f"{url_client}/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["id"] == user_id

def test_delete_user(client: TestClient, db: Session):
    # First, create a user
    response = client.post(
        url_client,
        json={"email": "testuser@example.com", "password": "testpassword"}
    )
    user_id = response.json()["id"]
    # Then, delete the created user
    response = client.delete(f"{url_client}/{user_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Verify the user is deleted
    response = client.get(f"{url_client}/{user_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

