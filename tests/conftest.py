# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.core.database import Base
from app.core.config import settings
from app.utils.token import get_db


@pytest.fixture(scope="session")
def create_test_db():
    admin_engine = create_engine( settings.POSTGRESQL_URL_ADMIN )
    print( settings.POSTGRESQL_URL_ADMIN, settings.POSTGRESQL_URL_TEST)
    
    with admin_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT") 
        conn.execute(text(f"CREATE DATABASE {settings.POSTGRESQL_DATABASE_NAME_TEST}")) 
    
    test_engine = create_engine(settings.POSTGRESQL_URL_TEST)
   
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    test_engine.dispose()

    with admin_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT") 
        conn.execute(text(f"DROP DATABASE {settings.POSTGRESQL_DATABASE_NAME_TEST}")) 
    
    admin_engine.dispose()


@pytest.fixture(scope="function")
def db(create_test_db):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=create_test_db)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback() 
        db.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    app.dependency_overrides.clear()


@pytest.fixture
def valid_api_key():
    return settings.API_KEY


@pytest.fixture
def test_user(db):
    from app.models.model import User
    from app.utils.token import get_password_hash
    
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "dni": "12345678",
        "username": "testuser",
        "date_born": "2000-01-01",
        "password": get_password_hash("testpassword")
    }
    
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@pytest.fixture
def test_user_super_admin(db):
    from app.models.model import User
    from app.utils.token import get_password_hash
    
    user_data_super_admin = {
        "first_name": "Test",
        "last_name": "User Super Admin",
        "dni": "75098777",
        "username": "testsuperadmin",
        "date_born": "2000-01-01",
        "password": get_password_hash("testpassword"),
        "type_user": "super_admin"
    }
    
    user_super_admin = User(**user_data_super_admin)
    db.add(user_super_admin)
    db.commit()
    db.refresh(user_super_admin)
    return user_super_admin


@pytest.fixture
def test_user_admin(db):
    from app.models.model import User
    from app.utils.token import get_password_hash
    
    user_data_super_admin = {
        "first_name": "Test",
        "last_name": "User Admin",
        "dni": "9876543",
        "username": "testsadmin",
        "date_born": "2000-01-01",
        "password": get_password_hash("testpassword"),
        "type_user": "admin"
    }
    
    user_admin = User(**user_data_super_admin)
    db.add(user_admin)
    db.commit()
    db.refresh(user_admin)
    return user_admin