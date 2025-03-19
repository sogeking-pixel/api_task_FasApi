from fastapi.testclient import TestClient
from app.core.config import settings
from fastapi import status
from app.models.model import User, Token
from sqlalchemy.orm import Session
from tests.main import url_admin, client_create, url_login

def get_token(client, data_login: dict)->str:
    response = client.post(
        url_login,
        data=data_login, 
    )
    return  response.json()['access_token'] 


def test_user_get_successful(client: TestClient, test_user: User, db: Session, test_user_admin: User, test_user_super_admin: User):
    
    login_data_admin = {
        "username": "testuser",
        "password": "testpassword"
    }
        
    
    login_data_super_admin = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    access_token_admin = get_token(client, login_data_admin )
    access_token_super_admin = get_token(client, login_data_super_admin )
    
    def verificate(token_user):
        response = client.get(
            f"{url_admin}/users",
            headers={"token":token_user},     
        )
        assert response.status_code == status.HTTP_200_OK
    
    verificate(access_token_admin)
    verificate(access_token_super_admin)
