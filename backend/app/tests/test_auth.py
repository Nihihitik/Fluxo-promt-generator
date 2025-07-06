import pytest
from datetime import datetime, timedelta
from models.user import User
from models.email_verification import EmailVerificationCode
from core.auth import verify_password, get_password_hash


class TestRegister:
    """Тесты для эндпоинта /auth/register"""
    
    def test_successful_registration(self, client):
        """Тест успешной регистрации"""
        response = client.post("/auth/register", json={
            "email": "newuser@example.com",
            "password": "password123",
            "name": "New User"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "Пользователь зарегистрирован!" in data["message"]
        assert "newuser@example.com" in data["message"]
        assert data["email_confirmed"] is False
    
    def test_registration_duplicate_email(self, client, test_user):
        """Тест регистрации с существующим email"""
        response = client.post("/auth/register", json={
            "email": test_user.email,
            "password": "password123",
            "name": "Duplicate User"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "уже существует" in data["detail"]
    
    def test_registration_invalid_email(self, client):
        """Тест регистрации с некорректным email"""
        response = client.post("/auth/register", json={
            "email": "invalid-email",
            "password": "password123",
            "name": "Test User"
        })
        
        assert response.status_code == 422
    
    def test_registration_short_password(self, client):
        """Тест регистрации с коротким паролем"""
        response = client.post("/auth/register", json={
            "email": "shortpass@example.com",
            "password": "123",
            "name": "Test User"
        })
        
        assert response.status_code == 422
    
    def test_registration_missing_fields(self, client):
        """Тест регистрации с отсутствующими полями"""
        response = client.post("/auth/register", json={
            "email": "test@example.com"
        })
        
        assert response.status_code == 422


class TestLogin:
    """Тесты для эндпоинта /auth/login"""
    
    def test_successful_login(self, client, test_user, test_user_data):
        """Тест успешной авторизации"""
        response = client.post("/auth/login", json={
            "email": test_user.email,
            "password": test_user_data["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_password(self, client, test_user):
        """Тест авторизации с неверным паролем"""
        response = client.post("/auth/login", json={
            "email": test_user.email,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "Неверный email или пароль" in data["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Тест авторизации несуществующего пользователя"""
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "Неверный email или пароль" in data["detail"]
    
    def test_login_invalid_data(self, client):
        """Тест авторизации с некорректными данными"""
        response = client.post("/auth/login", json={
            "email": "invalid-email",
            "password": ""
        })
        
        assert response.status_code == 422


class TestGetCurrentUser:
    """Тесты для эндпоинта /auth/me"""
    
    def test_get_current_user_success(self, client, test_user, auth_headers):
        """Тест получения информации о текущем пользователе"""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["id"] == test_user.id
        assert data["is_email_confirmed"] is True
        assert "daily_limit" in data
        assert "requests_today" in data
    
    def test_get_current_user_no_token(self, client):
        """Тест получения информации без токена"""
        response = client.get("/auth/me")
        
        assert response.status_code == 403
    
    def test_get_current_user_invalid_token(self, client, invalid_auth_headers):
        """Тест получения информации с невалидным токеном"""
        response = client.get("/auth/me", headers=invalid_auth_headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "Неверный токен" in data["detail"]
    
    def test_get_current_user_expired_token(self, client, expired_auth_headers):
        """Тест получения информации с истекшим токеном"""
        response = client.get("/auth/me", headers=expired_auth_headers)
        
        assert response.status_code == 401


class TestConfirmEmail:
    """Тесты для эндпоинта /auth/confirm-email"""
    
    def test_successful_email_confirmation(self, client, db, test_user_unconfirmed):
        """Тест успешного подтверждения email"""
        # Создаем код подтверждения
        verification_code = EmailVerificationCode(
            user_id=test_user_unconfirmed.id,
            code="123456",
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        db.add(verification_code)
        db.commit()
        
        response = client.post("/auth/confirm-email", json={
            "email": test_user_unconfirmed.email,
            "code": "123456"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "успешно подтвержден" in data["message"]
        assert data["email_confirmed"] is True
    
    def test_email_confirmation_wrong_code(self, client, db, test_user_unconfirmed):
        """Тест подтверждения email с неверным кодом"""
        # Создаем код подтверждения
        verification_code = EmailVerificationCode(
            user_id=test_user_unconfirmed.id,
            code="123456",
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        db.add(verification_code)
        db.commit()
        
        response = client.post("/auth/confirm-email", json={
            "email": test_user_unconfirmed.email,
            "code": "654321"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "Неверный или истекший код" in data["detail"]
    
    def test_email_confirmation_expired_code(self, client, db, test_user_unconfirmed):
        """Тест подтверждения email с истекшим кодом"""
        # Создаем истекший код
        verification_code = EmailVerificationCode(
            user_id=test_user_unconfirmed.id,
            code="123456",
            expires_at=datetime.utcnow() - timedelta(minutes=1)
        )
        db.add(verification_code)
        db.commit()
        
        response = client.post("/auth/confirm-email", json={
            "email": test_user_unconfirmed.email,
            "code": "123456"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "Неверный или истекший код" in data["detail"]
    
    def test_email_confirmation_already_confirmed(self, client, test_user):
        """Тест подтверждения уже подтвержденного email"""
        response = client.post("/auth/confirm-email", json={
            "email": test_user.email,
            "code": "123456"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "Email уже подтвержден" in data["detail"]
    
    def test_email_confirmation_nonexistent_user(self, client):
        """Тест подтверждения email несуществующего пользователя"""
        response = client.post("/auth/confirm-email", json={
            "email": "nonexistent@example.com",
            "code": "123456"
        })
        
        assert response.status_code == 404
        data = response.json()
        assert "Пользователь не найден" in data["detail"]


class TestResendConfirmation:
    """Тесты для эндпоинта /auth/resend-confirmation"""
    
    def test_successful_resend_confirmation(self, client, test_user_unconfirmed):
        """Тест успешной повторной отправки кода"""
        response = client.post("/auth/resend-confirmation", json={
            "email": test_user_unconfirmed.email
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "отправлен на ваш email" in data["message"]
    
    def test_resend_confirmation_nonexistent_user(self, client):
        """Тест повторной отправки для несуществующего пользователя"""
        response = client.post("/auth/resend-confirmation", json={
            "email": "nonexistent@example.com"
        })
        
        assert response.status_code == 404
        data = response.json()
        assert "Пользователь с таким email не найден" in data["detail"]
    
    def test_resend_confirmation_already_confirmed(self, client, test_user):
        """Тест повторной отправки для уже подтвержденного email"""
        response = client.post("/auth/resend-confirmation", json={
            "email": test_user.email
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "Email уже подтвержден" in data["detail"]
    
    def test_resend_confirmation_rate_limit(self, client, db, test_user_unconfirmed):
        """Тест лимита повторных отправок"""
        # Создаем 3 кода за последний час
        for i in range(3):
            verification_code = EmailVerificationCode(
                user_id=test_user_unconfirmed.id,
                code=f"12345{i}",
                expires_at=datetime.utcnow() + timedelta(minutes=15),
                created_at=datetime.utcnow()
            )
            db.add(verification_code)
        db.commit()
        
        response = client.post("/auth/resend-confirmation", json={
            "email": test_user_unconfirmed.email
        })
        
        assert response.status_code == 429
        data = response.json()
        assert "Превышен лимит отправки" in data["detail"]


class TestChangePassword:
    """Тесты для эндпоинта /auth/change-password"""
    
    def test_successful_password_change(self, client, test_user, test_user_data, auth_headers):
        """Тест успешной смены пароля"""
        response = client.post("/auth/change-password", 
                             headers=auth_headers,
                             json={
                                 "current_password": test_user_data["password"],
                                 "new_password": "newpassword123"
                             })
        
        assert response.status_code == 200
        data = response.json()
        assert "успешно изменен" in data["message"]
    
    def test_password_change_wrong_current_password(self, client, auth_headers):
        """Тест смены пароля с неверным текущим паролем"""
        response = client.post("/auth/change-password", 
                             headers=auth_headers,
                             json={
                                 "current_password": "wrongpassword",
                                 "new_password": "newpassword123"
                             })
        
        assert response.status_code == 400
        data = response.json()
        assert "Неверный текущий пароль" in data["detail"]
    
    def test_password_change_same_password(self, client, test_user_data, auth_headers):
        """Тест смены пароля на тот же пароль"""
        response = client.post("/auth/change-password", 
                             headers=auth_headers,
                             json={
                                 "current_password": test_user_data["password"],
                                 "new_password": test_user_data["password"]
                             })
        
        assert response.status_code == 400
        data = response.json()
        assert "должен отличаться от текущего" in data["detail"]
    
    def test_password_change_unauthorized(self, client):
        """Тест смены пароля без авторизации"""
        response = client.post("/auth/change-password", json={
            "current_password": "password123",
            "new_password": "newpassword123"
        })
        
        assert response.status_code == 403
    
    def test_password_change_invalid_token(self, client, invalid_auth_headers):
        """Тест смены пароля с невалидным токеном"""
        response = client.post("/auth/change-password", 
                             headers=invalid_auth_headers,
                             json={
                                 "current_password": "password123",
                                 "new_password": "newpassword123"
                             })
        
        assert response.status_code == 401
    
    def test_password_change_short_new_password(self, client, test_user_data, auth_headers):
        """Тест смены пароля на короткий пароль"""
        response = client.post("/auth/change-password", 
                             headers=auth_headers,
                             json={
                                 "current_password": test_user_data["password"],
                                 "new_password": "123"
                             })
        
        assert response.status_code == 422