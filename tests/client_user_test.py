from fastapi.testclient import TestClient
from app.core.config import settings
from fastapi import status
from app.models.model import User, Token
from sqlalchemy.orm import Session
from tests.main import url_client, client_create,url_login

def get_token(client, data_login: dict)->str:
    response = client.post(
        url_login,
        data=data_login, 
    )
    return  response.json()['access_token'] 


