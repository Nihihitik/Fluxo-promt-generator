from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from core.database import get_db
from core.prompt_generator import generate_prompt, get_available_styles
from routers.auth import get_current_user
from models.user import User
from models.prompt_request import PromptRequest
from schemas.user import UserResponse
from schemas.prompt_request import PromptRequestCreate, PromptRequestResponse

router = APIRouter(prefix="/prompts", tags=["prompts"])


def check_daily_limit(db: Session, user: User) -> bool:
    """Проверяет дневной лимит пользователя"""
    today = date.today()
    
    # Если это первый запрос или новый день, сбрасываем счетчик
    if user.last_request_date != today:
        user.requests_today = 0
        user.last_request_date = today
        db.commit()
    
    # Проверяем лимит
    if user.requests_today >= user.daily_limit:
        return False
    
    return True


def increment_user_requests(db: Session, user: User):
    """Увеличивает счетчик запросов пользователя"""
    user.requests_today += 1
    db.commit()


@router.post("/create", response_model=PromptRequestResponse)
async def create_prompt(
    raw_request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание нового промпта"""
    print(f"🎯 Получен запрос на создание промпта:")
    print(f"  - Content-Type: {raw_request.headers.get('content-type', 'не указан')}")
    print(f"  - Method: {raw_request.method}")
    print(f"  - URL: {raw_request.url}")
    print(f"  - User-Agent: {raw_request.headers.get('user-agent', 'не указан')[:100]}...")
    
    # Читаем JSON данные только один раз
    try:
        request_data = await raw_request.json()
        print(f"  - JSON данные: {request_data}")
        print(f"  - Тип JSON: {type(request_data)}")
        
        # Создаем Pydantic модель
        request = PromptRequestCreate(**request_data)
        print(f"  - Успешно создана Pydantic модель: {request}")
        
    except ValidationError as e:
        print(f"  - Ошибка валидации Pydantic: {e}")
        print(f"  - Детали ошибки: {e.errors()}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Ошибка валидации: {e.errors()}"
        )
    except Exception as e:
        print(f"  - Общая ошибка создания модели: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка обработки запроса: {str(e)}"
        )
    
    print(f"  - Пользователь: {current_user.email}")
    print(f"  - Промпт: {request.original_prompt}")
    print(f"  - Стиль: {request.style_id}")
    # Получаем полного пользователя из БД
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Проверяем дневной лимит
    if not check_daily_limit(db, user):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Превышен дневной лимит запросов ({user.daily_limit})"
        )
    
    # Проверяем валидность стиля, если указан
    if request.style_id:
        available_styles = get_available_styles()
        if request.style_id not in available_styles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный ID стиля. Доступные стили: 1-4"
            )
    
    # Генерируем промпт
    generated_prompt = await generate_prompt(request.original_prompt, request.style_id)
    
    # Создаем запись о запросе
    prompt_request = PromptRequest(
        user_id=user.id,
        original_prompt=request.original_prompt,
        style_id=request.style_id,
        generated_prompt=generated_prompt
    )
    
    db.add(prompt_request)
    
    # Увеличиваем счетчик запросов
    increment_user_requests(db, user)
    
    db.commit()
    db.refresh(prompt_request)
    
    return prompt_request


@router.get("/history", response_model=List[PromptRequestResponse])
async def get_user_history(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10,
    offset: int = 0
):
    """Получение истории промптов пользователя"""
    prompts = db.query(PromptRequest).filter(
        PromptRequest.user_id == current_user.id
    ).order_by(PromptRequest.created_at.desc()).offset(offset).limit(limit).all()
    
    return prompts


@router.get("/styles")
async def get_prompt_styles(
    current_user: UserResponse = Depends(get_current_user)
):
    """Получение доступных стилей промптов"""
    return get_available_styles()


@router.get("/limits")
async def get_user_limits(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о лимитах пользователя"""
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    today = date.today()
    # Если это новый день, сбрасываем счетчик
    if user.last_request_date != today:
        user.requests_today = 0
        user.last_request_date = today
        db.commit()
    
    return {
        "daily_limit": user.daily_limit,
        "requests_today": user.requests_today,
        "remaining_requests": user.daily_limit - user.requests_today,
        "last_request_date": user.last_request_date
    }