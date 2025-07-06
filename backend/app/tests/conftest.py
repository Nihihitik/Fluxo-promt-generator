import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from core.database import Base, get_db
from core.auth import create_access_token, get_password_hash
from models.user import User
from models.prompt_style import PromptStyle
from main import app

# Тестовая база данных SQLite в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Переопределяем зависимость для тестовой БД"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Создаем тестовую БД для каждого теста"""
    Base.metadata.create_all(bind=engine)
    
    # Создаем стили промптов
    db_session = TestingSessionLocal()
    if not db_session.query(PromptStyle).first():
        styles = [
            PromptStyle(id=1, name="Professional", description="Professional style"),
            PromptStyle(id=2, name="Creative", description="Creative style"),
            PromptStyle(id=3, name="Analytical", description="Analytical style"),
            PromptStyle(id=4, name="Simple", description="Simple style"),
        ]
        db_session.add_all(styles)
        db_session.commit()
    
    yield db_session
    db_session.close()
    
    # Очищаем БД после каждого теста
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Создаем тестовый клиент для каждого теста"""
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Данные для тестового пользователя"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }


@pytest.fixture
def test_user(db, test_user_data):
    """Создаем тестового пользователя в БД"""
    user = User(
        email=test_user_data["email"],
        password_hash=get_password_hash(test_user_data["password"]),
        name=test_user_data["name"],
        is_email_confirmed=True,
        daily_limit=10,
        requests_today=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_unconfirmed(db, test_user_data):
    """Создаем неподтвержденного пользователя"""
    user = User(
        email="unconfirmed@example.com",
        password_hash=get_password_hash(test_user_data["password"]),
        name=test_user_data["name"],
        is_email_confirmed=False,
        daily_limit=10,
        requests_today=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """Создаем JWT токен для тестового пользователя"""
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": test_user.email}, 
        expires_delta=access_token_expires
    )
    return access_token


@pytest.fixture
def auth_headers(auth_token):
    """Заголовки авторизации для тестов"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def invalid_auth_headers():
    """Недействительные заголовки авторизации"""
    return {"Authorization": "Bearer invalid_token"}


@pytest.fixture
def expired_auth_headers():
    """Истекший JWT токен"""
    expired_token = create_access_token(
        data={"sub": "test@example.com"}, 
        expires_delta=timedelta(minutes=-1)
    )
    return {"Authorization": f"Bearer {expired_token}"}


@pytest.fixture
def test_user_with_limit_reached(db, test_user_data):
    """Пользователь с исчерпанным лимитом запросов"""
    user = User(
        email="limited@example.com",
        password_hash=get_password_hash(test_user_data["password"]),
        name=test_user_data["name"],
        is_email_confirmed=True,
        daily_limit=3,
        requests_today=3,
        last_request_date=datetime.now().date()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Мокаем внешние сервисы для тестов
@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Мокаем внешние сервисы (email, OpenRouter API)"""
    def mock_send_verification_email(*args, **kwargs):
        return True
    
    def mock_send_welcome_email(*args, **kwargs):
        return True
    
    def mock_generate_prompt(prompt, style_id=None):
        return f"Generated prompt for: {prompt} (style: {style_id})"
    
    monkeypatch.setattr("services.email_service.send_verification_email", mock_send_verification_email)
    monkeypatch.setattr("services.email_service.send_welcome_email", mock_send_welcome_email)
    monkeypatch.setattr("core.prompt_generator.generate_prompt", mock_generate_prompt)