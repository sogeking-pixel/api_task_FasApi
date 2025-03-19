from fastapi.testclient import TestClient
from app.core.config import settings
from fastapi import status
from app.models.model import User, Token
from sqlalchemy.orm import Session
from tests.main import fake_key, real_key, url_login, url_sig_up, client_create



def test_root_nose(client: TestClient):
  response = client.get("/")
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == {"Hello": "World"}
  

def test_sign_up_incorrect_key(client: TestClient):
  response = client.post(url_sig_up , headers={"api-key": fake_key}, json=client_create)
  assert response.status_code == status.HTTP_401_UNAUTHORIZED
  assert response.json() == {"detail": "Inconrrect Key"}


def test_sign_up_invalid_date_format(client: TestClient):
  invalid_client = client_create.copy()
  invalid_client['date_born'] = "incorrect date"
  
  response = client.post(
    url_sig_up,
    headers={"api-key": real_key},
    json=invalid_client
  )
  
  assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
  response_data = response.json()
  assert "detail" in response_data


def test_sign_up_missing_required_field(client: TestClient):
  invalid_client = client_create.copy()
  del invalid_client['username']
  
  response = client.post(
    url_sig_up,
    headers={"api-key": real_key},
    json=invalid_client
  )
  
  assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_sign_up_no_api_key(client: TestClient):
  response = client.post(url_sig_up, json=client_create)
  assert response.status_code == status.HTTP_401_UNAUTHORIZED
  assert response.json()['detail'] == "The Key is missing"


def test_sign_up_empty_body(client: TestClient):
  response = client.post(
    url_sig_up,
    headers={"api-key": real_key},
    json={}
  )
  assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
  
  
  
def test_sign_up(client: TestClient):
    response = client.post(url_sig_up , headers={"api-key": real_key}, json=client_create)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['msg'] == 'create!'
    assert 'user' in response.json()
    assert "id" in response.json()['user']
    assert response.json()['user']['username'] == client_create['username']
    assert "password" not in response.json()['user']


def test_login_successful(client: TestClient, test_user: User, db: Session):
    
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    response = client.post(
        url_login,
        data=login_data, 
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    token_in_db = db.query(Token).filter(Token.user_id == test_user.id).first()
    assert token_in_db is not None
    assert token_in_db.access_token == response.json()["access_token"]


def test_login_wrong_password(client: TestClient):
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    
    response = client.post(
        url_login,
        data=login_data,
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Could not validate credentials"
    
    

def test_login_user_not_found(client: TestClient):
    login_data = {
        "username": "nonexistentuser",
        "password": "anypassword"
    }
    
    response = client.post(
        url_login,
        data=login_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Could not validate credentials"
    