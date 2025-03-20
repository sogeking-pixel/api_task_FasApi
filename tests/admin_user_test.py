from fastapi.testclient import TestClient
from app.core.config import settings
from fastapi import status
from app.models.model import User, Token
from sqlalchemy.orm import Session
from tests.main import url_admin, client_create, url_login, login_data_admin, login_data_super_admin

def get_token_and_type(client, data_login: dict)->list[str, str]:
    response = client.post(
        url_login,
        data=data_login, 
    )
    return response.json()['token_type'] , response.json()['access_token'] 

def create_new_client(db: Session, user_data: dict):
    from app.utils.token import get_password_hash    
    
    user_data['password'] = get_password_hash("testpassword")
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_user_get_successful(client: TestClient, db: Session, test_user_admin: User, test_user_super_admin: User, ):
    
    type_tokin_admin, access_token_admin = get_token_and_type(client, login_data_admin )
    type_token_super_admin, access_token_super_admin = get_token_and_type(client, login_data_super_admin )
    
    def verificate(type_token, token_user):
        response = client.get(
            f"{url_admin}/users",
            headers={"Authorization": f"{type_token} {token_user}"},     
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.json()
        assert 'next_link' in response.json()
        assert 'previous_link' in response.json()
        assert 'data' in response.json()
        
    verificate(type_tokin_admin, access_token_admin)
    verificate(type_token_super_admin, access_token_super_admin)


def test_user_get_unauthorized(client: TestClient, db: Session):
    response = client.get(f"{url_admin}/users")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(
        f"{url_admin}/users",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_get_forbidden(client: TestClient, db: Session, test_user: User):
    
    type_token, access_token = get_token_and_type(client, {
        "username": test_user.username,
        "password": "testpassword"
    })
    
    response = client.get(
        f"{url_admin}/users",
        headers={"Authorization": f"{type_token} {access_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_user_get_invalid_token_format(client: TestClient):
    response = client.get(
        f"{url_admin}/users",
        headers={"Authorization": "InvalidFormat token123"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.get(
        f"{url_admin}/users",
        headers={"Authorization": "Bearer"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
