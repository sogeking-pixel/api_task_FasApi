from fastapi.testclient import TestClient
from app.core.config import settings
from fastapi import status
from app.models.model import User, Token
from sqlalchemy.orm import Session
from tests.main import url_user, client_create, url_create_admin, url_me, url_login

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
            url_user,
            headers={"token":token_user},     
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
        token_in_db = db.query(Token).filter(Token.user_id == test_user.id).first()
        assert token_in_db is not None
        assert token_in_db.access_token == response.json()["access_token"]
