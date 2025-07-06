import pytest
from datetime import datetime, timedelta
from models.user import User
from models.email_verification import EmailVerificationCode
from models.prompt_request import PromptRequest
from core.auth import get_password_hash


class TestFullUserJourney:
    """Интеграционные тесты полного пути пользователя"""
    
    def test_complete_user_registration_flow(self, client, db):
        """Тест полного цикла регистрации и подтверждения email"""
        # 1. Регистрация пользователя
        registration_data = {
            "email": "integration@example.com",
            "password": "testpassword123",
            "name": "Integration User"
        }
        
        response = client.post("/auth/register", json=registration_data)
        assert response.status_code == 200
        
        # 2. Проверяем, что пользователь создан в БД
        user = db.query(User).filter(User.email == registration_data["email"]).first()
        assert user is not None
        assert user.is_email_confirmed is False
        
        # 3. Проверяем, что создан код подтверждения
        verification_code = db.query(EmailVerificationCode).filter(
            EmailVerificationCode.user_id == user.id
        ).first()
        assert verification_code is not None
        
        # 4. Подтверждаем email
        response = client.post("/auth/confirm-email", json={
            "email": registration_data["email"],
            "code": verification_code.code
        })
        assert response.status_code == 200
        
        # 5. Проверяем, что email подтвержден
        db.refresh(user)
        assert user.is_email_confirmed is True
        
        # 6. Авторизуемся
        response = client.post("/auth/login", json={
            "email": registration_data["email"],
            "password": registration_data["password"]
        })
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        
        # 7. Проверяем доступ к защищенным эндпоинтам
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        
        user_data = response.json()
        assert user_data["email"] == registration_data["email"]
    
    def test_full_prompt_generation_workflow(self, client, db):
        """Тест полного цикла создания и использования промптов"""
        # 1. Создаем и подтверждаем пользователя
        user = User(
            email="prompt@example.com",
            password_hash=get_password_hash("testpassword123"),
            name="Prompt User",
            is_email_confirmed=True,
            daily_limit=10,
            requests_today=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 2. Авторизуемся
        login_response = client.post("/auth/login", json={
            "email": "prompt@example.com",
            "password": "testpassword123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Получаем доступные стили
        styles_response = client.get("/prompts/styles", headers=headers)
        assert styles_response.status_code == 200
        
        styles = styles_response.json()
        assert len(styles) == 4
        
        # 4. Проверяем лимиты
        limits_response = client.get("/prompts/limits", headers=headers)
        assert limits_response.status_code == 200
        
        limits = limits_response.json()
        assert limits["daily_limit"] == 10
        assert limits["requests_today"] == 0
        assert limits["remaining_requests"] == 10
        
        # 5. Создаем первый промпт
        prompt1_response = client.post("/prompts/create", 
                                     headers=headers,
                                     json={
                                         "original_prompt": "Write a story about AI",
                                         "style_id": 1
                                     })
        assert prompt1_response.status_code == 200
        
        prompt1_data = prompt1_response.json()
        assert prompt1_data["original_prompt"] == "Write a story about AI"
        assert prompt1_data["style_id"] == 1
        assert "generated_prompt" in prompt1_data
        
        # 6. Создаем второй промпт без стиля
        prompt2_response = client.post("/prompts/create", 
                                     headers=headers,
                                     json={
                                         "original_prompt": "Explain quantum computing"
                                     })
        assert prompt2_response.status_code == 200
        
        # 7. Проверяем обновление лимитов
        limits_response = client.get("/prompts/limits", headers=headers)
        assert limits_response.status_code == 200
        
        limits = limits_response.json()
        assert limits["requests_today"] == 2
        assert limits["remaining_requests"] == 8
        
        # 8. Получаем историю промптов
        history_response = client.get("/prompts/history", headers=headers)
        assert history_response.status_code == 200
        
        history = history_response.json()
        assert len(history) == 2
        
        # Проверяем сортировку (новые сначала)
        assert history[0]["original_prompt"] == "Explain quantum computing"
        assert history[1]["original_prompt"] == "Write a story about AI"
        
        # 9. Тестируем пагинацию
        history_page_response = client.get("/prompts/history?limit=1&offset=0", headers=headers)
        assert history_page_response.status_code == 200
        
        history_page = history_page_response.json()
        assert len(history_page) == 1
        assert history_page[0]["original_prompt"] == "Explain quantum computing"
    
    def test_user_limit_enforcement_workflow(self, client, db):
        """Тест работы с лимитами пользователей"""
        # 1. Создаем пользователя с низким лимитом
        user = User(
            email="limited@example.com",
            password_hash=get_password_hash("testpassword123"),
            name="Limited User",
            is_email_confirmed=True,
            daily_limit=2,
            requests_today=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 2. Авторизуемся
        login_response = client.post("/auth/login", json={
            "email": "limited@example.com",
            "password": "testpassword123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Создаем промпты до лимита
        for i in range(2):
            response = client.post("/prompts/create", 
                                 headers=headers,
                                 json={
                                     "original_prompt": f"Prompt {i+1}",
                                     "style_id": 1
                                 })
            assert response.status_code == 200
        
        # 4. Проверяем, что лимит исчерпан
        limits_response = client.get("/prompts/limits", headers=headers)
        assert limits_response.status_code == 200
        
        limits = limits_response.json()
        assert limits["requests_today"] == 2
        assert limits["remaining_requests"] == 0
        
        # 5. Попытка создать еще один промпт должна быть отклонена
        response = client.post("/prompts/create", 
                             headers=headers,
                             json={
                                 "original_prompt": "Exceeded limit prompt",
                                 "style_id": 1
                             })
        assert response.status_code == 429
        
        # 6. Проверяем, что история содержит только разрешенные промпты
        history_response = client.get("/prompts/history", headers=headers)
        assert history_response.status_code == 200
        
        history = history_response.json()
        assert len(history) == 2
    
    def test_password_change_workflow(self, client, db):
        """Тест полного цикла смены пароля"""
        # 1. Создаем и подтверждаем пользователя
        user = User(
            email="password@example.com",
            password_hash=get_password_hash("oldpassword123"),
            name="Password User",
            is_email_confirmed=True,
            daily_limit=10,
            requests_today=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 2. Авторизуемся со старым паролем
        login_response = client.post("/auth/login", json={
            "email": "password@example.com",
            "password": "oldpassword123"
        })
        assert login_response.status_code == 200
        
        old_token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {old_token}"}
        
        # 3. Меняем пароль
        change_response = client.post("/auth/change-password", 
                                    headers=headers,
                                    json={
                                        "current_password": "oldpassword123",
                                        "new_password": "newpassword123"
                                    })
        assert change_response.status_code == 200
        
        # 4. Проверяем, что старый пароль больше не работает
        login_response = client.post("/auth/login", json={
            "email": "password@example.com",
            "password": "oldpassword123"
        })
        assert login_response.status_code == 401
        
        # 5. Проверяем, что новый пароль работает
        login_response = client.post("/auth/login", json={
            "email": "password@example.com",
            "password": "newpassword123"
        })
        assert login_response.status_code == 200
        
        new_token = login_response.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        
        # 6. Проверяем доступ к защищенным эндпоинтам с новым токеном
        response = client.get("/auth/me", headers=new_headers)
        assert response.status_code == 200


class TestErrorHandlingAndEdgeCases:
    """Тесты обработки ошибок и граничных случаев"""
    
    def test_concurrent_email_confirmations(self, client, db):
        """Тест одновременного подтверждения email"""
        # Создаем неподтвержденного пользователя
        user = User(
            email="concurrent@example.com",
            password_hash=get_password_hash("testpassword123"),
            name="Concurrent User",
            is_email_confirmed=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Создаем код подтверждения
        verification_code = EmailVerificationCode(
            user_id=user.id,
            code="123456",
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        db.add(verification_code)
        db.commit()
        
        # Первое подтверждение должно пройти
        response1 = client.post("/auth/confirm-email", json={
            "email": "concurrent@example.com",
            "code": "123456"
        })
        assert response1.status_code == 200
        
        # Второе подтверждение должно быть отклонено
        response2 = client.post("/auth/confirm-email", json={
            "email": "concurrent@example.com",
            "code": "123456"
        })
        assert response2.status_code == 400
        assert "Email уже подтвержден" in response2.json()["detail"]
    
    def test_token_expiration_handling(self, client, db):
        """Тест обработки истекших токенов"""
        # Создаем пользователя
        user = User(
            email="expired@example.com",
            password_hash=get_password_hash("testpassword123"),
            name="Expired User",
            is_email_confirmed=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Создаем истекший токен
        from core.auth import create_access_token
        expired_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=-1)
        )
        
        expired_headers = {"Authorization": f"Bearer {expired_token}"}
        
        # Попытка доступа к защищенным эндпоинтам должна быть отклонена
        response = client.get("/auth/me", headers=expired_headers)
        assert response.status_code == 401
        
        response = client.get("/prompts/history", headers=expired_headers)
        assert response.status_code == 401
        
        response = client.post("/prompts/create", 
                             headers=expired_headers,
                             json={
                                 "original_prompt": "Test prompt",
                                 "style_id": 1
                             })
        assert response.status_code == 401
    
    def test_invalid_style_id_handling(self, client, db):
        """Тест обработки невалидных ID стилей"""
        # Создаем авторизованного пользователя
        user = User(
            email="style@example.com",
            password_hash=get_password_hash("testpassword123"),
            name="Style User",
            is_email_confirmed=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Авторизуемся
        login_response = client.post("/auth/login", json={
            "email": "style@example.com",
            "password": "testpassword123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Тестируем различные невалидные ID стилей
        invalid_styles = [0, 5, 999, -1, "invalid", None]
        
        for style_id in invalid_styles:
            if style_id is None:
                continue  # None является валидным (отсутствие стиля)
            
            response = client.post("/prompts/create", 
                                 headers=headers,
                                 json={
                                     "original_prompt": "Test prompt",
                                     "style_id": style_id
                                 })
            
            if isinstance(style_id, str):
                # Строковые ID должны вызывать ошибку валидации
                assert response.status_code == 422
            else:
                # Числовые ID вне диапазона должны вызывать ошибку бизнес-логики
                assert response.status_code == 400
                assert "Неверный ID стиля" in response.json()["detail"]


class TestDataConsistency:
    """Тесты целостности данных"""
    
    def test_user_prompt_relationship(self, client, db):
        """Тест связи между пользователем и промптами"""
        # Создаем пользователя
        user = User(
            email="relationship@example.com",
            password_hash=get_password_hash("testpassword123"),
            name="Relationship User",
            is_email_confirmed=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Авторизуемся
        login_response = client.post("/auth/login", json={
            "email": "relationship@example.com",
            "password": "testpassword123"
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Создаем промпт
        response = client.post("/prompts/create", 
                             headers=headers,
                             json={
                                 "original_prompt": "Test relationship",
                                 "style_id": 1
                             })
        assert response.status_code == 200
        
        prompt_data = response.json()
        
        # Проверяем, что промпт связан с правильным пользователем
        assert prompt_data["user_id"] == user.id
        
        # Проверяем в БД
        prompt = db.query(PromptRequest).filter(
            PromptRequest.id == prompt_data["id"]
        ).first()
        assert prompt is not None
        assert prompt.user_id == user.id
        assert prompt.user.email == user.email
    
    def test_verification_code_cleanup(self, client, db):
        """Тест очистки кодов подтверждения"""
        # Создаем пользователя
        user = User(
            email="cleanup@example.com",
            password_hash=get_password_hash("testpassword123"),
            name="Cleanup User",
            is_email_confirmed=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Создаем несколько кодов
        codes = []
        for i in range(3):
            code = EmailVerificationCode(
                user_id=user.id,
                code=f"12345{i}",
                expires_at=datetime.utcnow() + timedelta(minutes=15)
            )
            codes.append(code)
            db.add(code)
        db.commit()
        
        # Проверяем, что все коды активны
        active_codes = db.query(EmailVerificationCode).filter(
            EmailVerificationCode.user_id == user.id,
            EmailVerificationCode.is_used == False
        ).all()
        assert len(active_codes) == 3
        
        # Повторно отправляем код подтверждения
        response = client.post("/auth/resend-confirmation", json={
            "email": "cleanup@example.com"
        })
        assert response.status_code == 200
        
        # Проверяем, что старые коды деактивированы
        active_codes = db.query(EmailVerificationCode).filter(
            EmailVerificationCode.user_id == user.id,
            EmailVerificationCode.is_used == False
        ).all()
        assert len(active_codes) == 1  # Только новый код должен быть активен