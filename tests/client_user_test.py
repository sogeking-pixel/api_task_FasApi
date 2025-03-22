from fastapi.testclient import TestClient
from app.core.config import settings
from fastapi import status
from app.models.model import User, Token
from sqlalchemy.orm import Session
from tests.main import url_client, client_create, url_login, login_data_admin, login_data_super_admin, login_data_user
from tests.admin_user_test import get_token_and_type



def test_user_me_successful(client: TestClient, db: Session, test_user_admin: User, test_user_super_admin: User, test_user: User):
    
    type_tokin_admin, access_token_admin = get_token_and_type(client, login_data_admin )
    type_token_super_admin, access_token_super_admin = get_token_and_type(client, login_data_super_admin )
    type_token, access_token = get_token_and_type(client, login_data_user)
    
    def verificate(type_token, token_user, user: User):
        response = client.get(
            f"{url_client}/me",
            headers={"Authorization": f"{type_token} {token_user}"},     
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'id' in response.json() and response.json()['id'] == user.id
        assert 'username' in response.json() and response.json()['username'] == user.username
        
    verificate(type_tokin_admin, access_token_admin, test_user_admin)
    verificate(type_token_super_admin, access_token_super_admin, test_user_super_admin)
    verificate(type_token, access_token, test_user)
    
def test_user_get_unauthorized(client: TestClient, db: Session):
    response = client.get(f"{url_client}/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(
        f"{url_client}/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_user_get_invalid_token_format(client: TestClient):
    response = client.get(
        f"{url_client}/me",
        headers={"Authorization": "InvalidFormat token123"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.get(
        f"{url_client}/me",
        headers={"Authorization": "Bearer"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED



def test_user_change_password_successful(client: TestClient, db: Session, test_user_super_admin: User, test_user_admin: User, test_user: User):
    # Test super admin can change any user's password
    type_token_super_admin, access_token_super_admin = get_token_and_type(client, login_data_super_admin)
    test_cases = [test_user_admin.id, test_user.id, test_user_super_admin.id]
    for user_id in test_cases:
        response = client.patch(
            f"{url_client}/{user_id}/password",
            headers={"Authorization": f"{type_token_super_admin} {access_token_super_admin}"},
            json="new_password123"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"msg": "Password updated successfully!"}
    
    login_data_admin['password'] = "new_password123"
    # Test admin can change only client's password
    type_token_admin, access_token_admin = get_token_and_type(client, login_data_admin)
    response = client.patch(
        f"{url_client}/{test_user.id}/password",
        headers={"Authorization": f"{type_token_admin} {access_token_admin}"},
        json="new_password456"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "Password updated successfully!"}
    
    # Test client can only change their own password
    login_data_user['password'] = "new_password456"
    type_token_user, access_token_user = get_token_and_type(client, login_data_user)
    response = client.patch(
        f"{url_client}/{test_user.id}/password",
        headers={"Authorization": f"{type_token_user} {access_token_user}"},
        json="new_password789"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "Password updated successfully!"}
    
def test_user_change_password_forbidden(client: TestClient, db: Session, test_user: User, test_user_admin: User):
    type_token_admin, access_token_admin = get_token_and_type(client, login_data_admin)
    type_token_user, access_token_user = get_token_and_type(client, login_data_user)
    
    # Test client cannot change other users' passwords
    response = client.patch(
        f"{url_client}/{test_user_admin.id}/password",
        headers={"Authorization": f"{type_token_user} {access_token_user}"},
        json="new_password123"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # Test admin cannot change admin's password
    response = client.patch(
        f"{url_client}/{test_user_admin.id}/password", 
        headers={"Authorization": f"{type_token_admin} {access_token_admin}"},
        json="new_password123"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Test with non-existent user
    response = client.patch(
        f"{url_client}/99999/password",
        headers={"Authorization": f"{type_token_admin} {access_token_admin}"},
        json="new_password123"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_user_change_password_unauthorized(client: TestClient, db: Session):
    response = client.patch(f"{url_client}/1/password")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.patch(
        f"{url_client}/1/password",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_user_change_password_invalid_token_format(client: TestClient):
    response = client.patch(
       f"{url_client}/1/password",
        headers={"Authorization": "InvalidFormat token123"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.patch(
        f"{url_client}/1/password",
        headers={"Authorization": "Bearer"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    