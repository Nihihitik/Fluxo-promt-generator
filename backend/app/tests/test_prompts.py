import pytest
from datetime import datetime, date
from models.user import User
from models.prompt_request import PromptRequest
from models.prompt_style import PromptStyle
from core.auth import get_password_hash, create_access_token


class TestCreatePrompt:
    """Тесты для эндпоинта /prompts/create"""
    
    def test_successful_prompt_creation(self, client, test_user, auth_headers):
        """Тест успешного создания промпта"""
        response = client.post("/prompts/create", 
                             headers=auth_headers,
                             json={
                                 "original_prompt": "Write a story about a robot",
                                 "style_id": 1
                             })
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_prompt"] == "Write a story about a robot"
        assert data["style_id"] == 1
        assert data["user_id"] == test_user.id
        assert "generated_prompt" in data
        assert data["generated_prompt"] is not None
        assert "id" in data
        assert "created_at" in data
    
    def test_prompt_creation_without_style(self, client, test_user, auth_headers):
        """Тест создания промпта без указания стиля"""
        response = client.post("/prompts/create", 
                             headers=auth_headers,
                             json={
                                 "original_prompt": "Write a story about a robot"
                             })
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_prompt"] == "Write a story about a robot"
        assert data["style_id"] is None
        assert data["user_id"] == test_user.id
        assert "generated_prompt" in data
    
    def test_prompt_creation_invalid_style(self, client, auth_headers):
        """Тест создания промпта с невалидным стилем"""
        response = client.post("/prompts/create", 
                             headers=auth_headers,
                             json={
                                 "original_prompt": "Write a story about a robot",
                                 "style_id": 999
                             })
        
        assert response.status_code == 400
        data = response.json()
        assert "Неверный ID стиля" in data["detail"]
    
    def test_prompt_creation_empty_prompt(self, client, auth_headers):
        """Тест создания промпта с пустым текстом"""
        response = client.post("/prompts/create", 
                             headers=auth_headers,
                             json={
                                 "original_prompt": "",
                                 "style_id": 1
                             })
        
        assert response.status_code == 422
    
    def test_prompt_creation_unauthorized(self, client):
        """Тест создания промпта без авторизации"""
        response = client.post("/prompts/create", json={
            "original_prompt": "Write a story about a robot",
            "style_id": 1
        })
        
        assert response.status_code == 403
    
    def test_prompt_creation_invalid_token(self, client, invalid_auth_headers):
        """Тест создания промпта с невалидным токеном"""
        response = client.post("/prompts/create", 
                             headers=invalid_auth_headers,
                             json={
                                 "original_prompt": "Write a story about a robot",
                                 "style_id": 1
                             })
        
        assert response.status_code == 401
    
    def test_prompt_creation_daily_limit_exceeded(self, client, db, test_user_data):
        """Тест создания промпта при превышении дневного лимита"""
        # Создаем пользователя с исчерпанным лимитом
        user = User(
            email="limited@example.com",
            password_hash=get_password_hash(test_user_data["password"]),
            name="Limited User",
            is_email_confirmed=True,
            daily_limit=3,
            requests_today=3,
            last_request_date=date.today()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Создаем токен для этого пользователя
        token = create_access_token(data={"sub": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/prompts/create", 
                             headers=headers,
                             json={
                                 "original_prompt": "Write a story about a robot",
                                 "style_id": 1
                             })
        
        assert response.status_code == 429
        data = response.json()
        assert "Превышен дневной лимит" in data["detail"]
    
    def test_prompt_creation_increments_counter(self, client, db, test_user, auth_headers):
        """Тест увеличения счетчика запросов при создании промпта"""
        # Получаем изначальное количество запросов
        initial_requests = test_user.requests_today
        
        response = client.post("/prompts/create", 
                             headers=auth_headers,
                             json={
                                 "original_prompt": "Write a story about a robot",
                                 "style_id": 1
                             })
        
        assert response.status_code == 200
        
        # Обновляем пользователя из БД
        db.refresh(test_user)
        assert test_user.requests_today == initial_requests + 1
    
    def test_prompt_creation_missing_data(self, client, auth_headers):
        """Тест создания промпта с отсутствующими данными"""
        response = client.post("/prompts/create", 
                             headers=auth_headers,
                             json={})
        
        assert response.status_code == 422


class TestGetUserHistory:
    """Тесты для эндпоинта /prompts/history"""
    
    def test_get_empty_history(self, client, test_user, auth_headers):
        """Тест получения пустой истории"""
        response = client.get("/prompts/history", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_history_with_prompts(self, client, db, test_user, auth_headers):
        """Тест получения истории с промптами"""
        # Создаем несколько промптов
        prompts = [
            PromptRequest(
                user_id=test_user.id,
                original_prompt="First prompt",
                style_id=1,
                generated_prompt="Generated first prompt"
            ),
            PromptRequest(
                user_id=test_user.id,
                original_prompt="Second prompt",
                style_id=2,
                generated_prompt="Generated second prompt"
            )
        ]
        
        for prompt in prompts:
            db.add(prompt)
        db.commit()
        
        response = client.get("/prompts/history", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Проверяем что запросы отсортированы по дате создания (новые сначала)
        assert data[0]["original_prompt"] == "Second prompt"
        assert data[1]["original_prompt"] == "First prompt"
    
    def test_get_history_with_pagination(self, client, db, test_user, auth_headers):
        """Тест получения истории с пагинацией"""
        # Создаем больше промптов, чем лимит по умолчанию
        for i in range(15):
            prompt = PromptRequest(
                user_id=test_user.id,
                original_prompt=f"Prompt {i}",
                style_id=1,
                generated_prompt=f"Generated prompt {i}"
            )
            db.add(prompt)
        db.commit()
        
        # Тест с лимитом
        response = client.get("/prompts/history?limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        
        # Тест с offset
        response = client.get("/prompts/history?limit=5&offset=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
    
    def test_get_history_unauthorized(self, client):
        """Тест получения истории без авторизации"""
        response = client.get("/prompts/history")
        assert response.status_code == 403
    
    def test_get_history_invalid_token(self, client, invalid_auth_headers):
        """Тест получения истории с невалидным токеном"""
        response = client.get("/prompts/history", headers=invalid_auth_headers)
        assert response.status_code == 401
    
    def test_get_history_only_user_prompts(self, client, db, test_user, auth_headers):
        """Тест получения истории только текущего пользователя"""
        # Создаем другого пользователя
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("password123"),
            name="Other User",
            is_email_confirmed=True
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
        
        # Создаем промпты для разных пользователей
        user_prompt = PromptRequest(
            user_id=test_user.id,
            original_prompt="User prompt",
            style_id=1,
            generated_prompt="User generated prompt"
        )
        other_prompt = PromptRequest(
            user_id=other_user.id,
            original_prompt="Other user prompt",
            style_id=1,
            generated_prompt="Other user generated prompt"
        )
        
        db.add(user_prompt)
        db.add(other_prompt)
        db.commit()
        
        response = client.get("/prompts/history", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["original_prompt"] == "User prompt"
        assert data[0]["user_id"] == test_user.id


class TestGetPromptStyles:
    """Тесты для эндпоинта /prompts/styles"""
    
    def test_get_styles_success(self, client, auth_headers):
        """Тест успешного получения стилей"""
        response = client.get("/prompts/styles", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 4
        
        # Проверяем что все стили присутствуют
        assert 1 in data
        assert 2 in data
        assert 3 in data
        assert 4 in data
    
    def test_get_styles_unauthorized(self, client):
        """Тест получения стилей без авторизации"""
        response = client.get("/prompts/styles")
        assert response.status_code == 403
    
    def test_get_styles_invalid_token(self, client, invalid_auth_headers):
        """Тест получения стилей с невалидным токеном"""
        response = client.get("/prompts/styles", headers=invalid_auth_headers)
        assert response.status_code == 401


class TestGetUserLimits:
    """Тесты для эндпоинта /prompts/limits"""
    
    def test_get_limits_success(self, client, test_user, auth_headers):
        """Тест успешного получения лимитов"""
        response = client.get("/prompts/limits", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "daily_limit" in data
        assert "requests_today" in data
        assert "remaining_requests" in data
        assert "last_request_date" in data
        
        assert data["daily_limit"] == test_user.daily_limit
        assert data["requests_today"] == test_user.requests_today
        assert data["remaining_requests"] == test_user.daily_limit - test_user.requests_today
    
    def test_get_limits_reset_for_new_day(self, client, db, test_user_data):
        """Тест сброса лимитов для нового дня"""
        # Создаем пользователя с данными за предыдущий день
        user = User(
            email="yesterday@example.com",
            password_hash=get_password_hash(test_user_data["password"]),
            name="Yesterday User",
            is_email_confirmed=True,
            daily_limit=10,
            requests_today=5,
            last_request_date=date.today().replace(day=1)  # Прошлый день
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Создаем токен для этого пользователя
        token = create_access_token(data={"sub": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/prompts/limits", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["requests_today"] == 0  # Должно сброситься
        assert data["remaining_requests"] == data["daily_limit"]
    
    def test_get_limits_unauthorized(self, client):
        """Тест получения лимитов без авторизации"""
        response = client.get("/prompts/limits")
        assert response.status_code == 403
    
    def test_get_limits_invalid_token(self, client, invalid_auth_headers):
        """Тест получения лимитов с невалидным токеном"""
        response = client.get("/prompts/limits", headers=invalid_auth_headers)
        assert response.status_code == 401


class TestPromptLimitBehavior:
    """Тесты поведения дневных лимитов"""
    
    def test_daily_limit_reset_on_new_day(self, client, db, test_user_data):
        """Тест сброса дневного лимита при наступлении нового дня"""
        # Создаем пользователя с данными за вчерашний день
        user = User(
            email="reset@example.com",
            password_hash=get_password_hash(test_user_data["password"]),
            name="Reset User",
            is_email_confirmed=True,
            daily_limit=3,
            requests_today=3,
            last_request_date=date.today().replace(day=1)  # Прошлый день
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Создаем токен для этого пользователя
        token = create_access_token(data={"sub": user.email})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Попытаемся создать промпт - должно сработать, т.к. лимит должен сброситься
        response = client.post("/prompts/create", 
                             headers=headers,
                             json={
                                 "original_prompt": "Test prompt after reset",
                                 "style_id": 1
                             })
        
        assert response.status_code == 200
        
        # Проверяем что лимит сбросился
        db.refresh(user)
        assert user.requests_today == 1
        assert user.last_request_date == date.today()
    
    def test_multiple_prompts_within_limit(self, client, db, test_user, auth_headers):
        """Тест создания нескольких промптов в рамках лимита"""
        # Убедимся что у пользователя есть лимит
        test_user.daily_limit = 5
        test_user.requests_today = 0
        db.commit()
        
        # Создаем несколько промптов
        for i in range(3):
            response = client.post("/prompts/create", 
                                 headers=auth_headers,
                                 json={
                                     "original_prompt": f"Test prompt {i}",
                                     "style_id": 1
                                 })
            assert response.status_code == 200
        
        # Проверяем что счетчик обновился
        db.refresh(test_user)
        assert test_user.requests_today == 3
    
    def test_prompt_creation_at_limit_boundary(self, client, db, test_user, auth_headers):
        """Тест создания промпта на границе лимита"""
        # Устанавливаем лимит в 1 запрос
        test_user.daily_limit = 1
        test_user.requests_today = 0
        db.commit()
        
        # Первый запрос должен пройти
        response = client.post("/prompts/create", 
                             headers=auth_headers,
                             json={
                                 "original_prompt": "First prompt",
                                 "style_id": 1
                             })
        assert response.status_code == 200
        
        # Второй запрос должен быть отклонен
        response = client.post("/prompts/create", 
                             headers=auth_headers,
                             json={
                                 "original_prompt": "Second prompt",
                                 "style_id": 1
                             })
        assert response.status_code == 429