from app.core.config import settings
from fastapi import status
import pytest

fake_key = "xdfdafasdfasdfasd"
real_key = settings.API_KEY
prefix = settings.API_PREFIX + "/auth"


client_create = {
  "first_name": "string",
  "last_name": "string",
  "dni": "string",
  "username": "string",
  "date_born": "2025-03-17",
  "password": "string"
}


def test_root_nose(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Hello": "World"}
    

def test_sign_up(client):
    url = prefix+'/sign-up/'
    print(url)
    response = client.post(url , headers={"api-key": fake_key}, json=client_create)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Inconrrect Key"}