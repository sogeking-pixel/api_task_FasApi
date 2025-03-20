from fastapi.testclient import TestClient
from app.core.config import settings
from fastapi import status
from app.models.model import User, Token
from sqlalchemy.orm import Session
from tests.main import url_admin, client_create, url_login, login_data_admin, login_data_super_admin, login_data_user

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
    
    type_token, access_token = get_token_and_type(client, login_data_user)
    
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



def test_user_created_admin_successful(client: TestClient, db: Session, test_user_super_admin: User):
    type_token, access_token =  get_token_and_type(client, login_data_super_admin)
    data_admin = {
        "first_name" : "first name test",
        "last_name" : "last name test",
        "dni" : "87677777",
        "username" : "test_admin_router",
        "password" : "testpassword",
        "date_born" : "2000-01-01" 
    }
    print(f"{type_token} {access_token}")
    response =  client.post(url=f"{url_admin}/create_admin" ,headers={"Authorization": f"{type_token} {access_token}"}, json=data_admin)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert 'msg' in response.json() and response.json()['msg'] == 'create!'
    assert "id" in response.json()['user'] 
    assert 'user' in response.json()
    assert response.json()['user']['username'] == data_admin['username']
    assert "password" not in response.json()['user']
    
def test_user_created_admin_forbidden(client: TestClient, db: Session, test_user: User, test_user_admin: User):
    type_tokin_admin, access_token_admin = get_token_and_type(client, login_data_admin )
    type_token_user, access_token_user = get_token_and_type(client, login_data_user )
    
    def verificate(type_token, token_user):
        response = client.post(
            f"{url_admin}/create_admin",
            headers={"Authorization": f"{type_token} {token_user}"},     
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    verificate(type_tokin_admin, access_token_admin)
    verificate(type_token_user, access_token_user)

def test_user_created_admin_unauthorized(client: TestClient, db: Session):
    response = client.post(f"{url_admin}/create_admin")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.post(
        f"{url_admin}/create_admin",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_user_created_admin_invalid_token_format(client: TestClient):
    response = client.post(
        f"{url_admin}/create_admin",
        headers={"Authorization": "InvalidFormat token123"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.post(
        f"{url_admin}/create_admin",
        headers={"Authorization": "Bearer"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    

def test_user_delete_successful(client: TestClient, db: Session, test_user_super_admin: User, test_user: User):
    type_token, access_token = get_token_and_type(client, login_data_super_admin)
    response = client.delete(
        f"{url_admin}/users/{test_user.id}",
        headers={"Authorization": f"{type_token} {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'msg' in response.json() and response.json()['msg'] == 'deleted!'

def test_user_delete_admin_forbidden(client: TestClient, db: Session, test_user: User, test_user_admin: User):
    type_token_admin, access_token_admin = get_token_and_type(client, login_data_admin)
    type_token_user, access_token_user = get_token_and_type(client, login_data_user)
    
    def verificate(type_token, token_user):
        response = client.delete(
            f"{url_admin}/users/{test_user_admin.id}",
            headers={"Authorization": f"{type_token} {token_user}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    verificate(type_token_admin, access_token_admin)
    verificate(type_token_user, access_token_user)

def test_user_delete_admin_unauthorized(client: TestClient, db: Session):
    response = client.delete(f"{url_admin}/users/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.delete(
        f"{url_admin}/users/1",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_user_delete_admin_invalid_token_format(client: TestClient):
    response = client.delete(
        f"{url_admin}/users/1",
        headers={"Authorization": "InvalidFormat token123"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.delete(
        f"{url_admin}/users/1",
        headers={"Authorization": "Bearer"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED



def test_get_only_user_successful(client: TestClient, db: Session, test_user_super_admin: User, test_user: User, test_user_admin: User):
    type_token_admin, access_token_admin = get_token_and_type(client, login_data_admin)
    type_token_super_admin, access_token_super_admin = get_token_and_type(client, login_data_super_admin)
    
    def verificate(type_token, access_token):
        response = client.get(
            f"{url_admin}/users/{test_user.id}",
            headers={"Authorization": f"{type_token} {access_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'id' in response.json()
        assert response.json()['username'] == test_user.username 
        
    verificate(type_token_admin, access_token_admin)
    verificate(type_token_super_admin, access_token_super_admin)
    
def test_get_only_user_forbidden(client: TestClient, db: Session, test_user: User, test_user_admin: User):
    type_token_user, access_token_user = get_token_and_type(client, login_data_user)
    
    response = client.get(
        f"{url_admin}/users/{test_user_admin.id}",
        headers={"Authorization": f"{type_token_user} {access_token_user}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN 

def test_get_only_user_unauthorized(client: TestClient, db: Session):
    response = client.get(f"{url_admin}/users/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(
        f"{url_admin}/users/1",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_only_user_invalid_token_format(client: TestClient):
    response = client.get(
        f"{url_admin}/users/1",
        headers={"Authorization": "InvalidFormat token123"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    response = client.get(
        f"{url_admin}/users/1",
        headers={"Authorization": "Bearer"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED



def test_user_change_status_successful(client: TestClient, db: Session, test_user_super_admin: User, test_user: User, test_user_admin: User):
    type_token_admin, access_token_admin = get_token_and_type(client, login_data_admin)
    type_token_super_admin, access_token_super_admin = get_token_and_type(client, login_data_super_admin)
    list_status =  ['suspense', 'banned', 'activate']
    
    def update_for_admin(status_user: str):
        response = client.patch(
            f"{url_admin}/users/{test_user.id}/status",params = {'status' :status_user},
            headers={"Authorization": f"{type_token_admin} {access_token_admin}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'msg' in response.json() and response.json()['msg'] == "update status user!"
        assert test_user.status_account == status_user
    
    def update_for_superadmin(status_user: str):
        response = client.patch(
            f"{url_admin}/users/{test_user_admin.id}/status",params = {'status' :status_user},
            headers={"Authorization": f"{type_token_super_admin} {access_token_super_admin}"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'msg' in response.json() and response.json()['msg'] == "update status user!"
        assert test_user_admin.status_account == status_user
    
    for status_user in list_status:
        update_for_admin(status_user)
    
    for status_user in list_status:
        update_for_superadmin(status_user)

def test_user_change_status_forbidden(client: TestClient, db: Session, test_user: User, test_user_admin: User):
    type_token_user, access_token_user = get_token_and_type(client, login_data_user)
    list_status = ['suspense', 'banned', 'activate']
    
    for status_user in list_status:
        response = client.patch(
            f"{url_admin}/users/{test_user_admin.id}/status", params={'status': status_user},
            headers={"Authorization": f"{type_token_user} {access_token_user}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

def test_user_change_status_unauthorized(client: TestClient, db: Session):
    list_status = ['suspense', 'banned', 'activate']
    
    for status_user in list_status:
        response = client.patch(
            f"{url_admin}/users/1/status", params={'status': status_user}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.patch(
            f"{url_admin}/users/1/status", params={'status': status_user},
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_user_change_status_invalid_token_format(client: TestClient):
    list_status = ['suspense', 'banned', 'activate']
    
    for status_user in list_status:
        response = client.patch(
            f"{url_admin}/users/1/status", params={'status': status_user},
            headers={"Authorization": "InvalidFormat token123"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.patch(
            f"{url_admin}/users/1/status", params={'status': status_user},
            headers={"Authorization": "Bearer"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED     