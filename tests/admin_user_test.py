from fastapi.testclient import TestClient
from app.core.config import settings
from fastapi import status
from app.models.model import User, Token
from sqlalchemy.orm import Session
from tests.main import url_admin, client_create, url_login

def get_token_and_type(client, data_login: dict)->list[str, str]:
    response = client.post(
        url_login,
        data=data_login, 
    )
    return response.json()['token_type'] , response.json()['access_token'] 


def test_user_get_successful(client: TestClient, db: Session, test_user_admin: User, test_user_super_admin: User):
    
    
    login_data_admin = {
        "username": "testsadmin",
        "password": "testpassword"
    }
        
    
    login_data_super_admin = {
        "username": "testsuperadmin",
        "password": "testpassword"
    }
    
    type_tokin_admin, access_token_admin = get_token_and_type(client, login_data_admin )
    type_token_super_admin, access_token_super_admin = get_token_and_type(client, login_data_super_admin )
    
    def verificate(type_token, token_user):
        response = client.get(
            f"{url_admin}/users",
            headers={"Authorization": f"{type_token} {token_user}"},     
        )
        assert response.status_code == status.HTTP_200_OK
    
    verificate(type_tokin_admin, access_token_admin)
    verificate(type_token_super_admin, access_token_super_admin)
