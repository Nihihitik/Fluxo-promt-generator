from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import (
    authenticate_user,
    create_user,
    create_access_token,
    verify_token,
    get_user_by_email,
    change_user_password,
    send_verification_code,
    verify_email_code,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from schemas.user import UserCreate, UserLogin, UserResponse, Token, EmailConfirmation, EmailConfirmationRequest, EmailConfirmationResponse, PasswordChange, PasswordChangeResponse
from models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/register", response_model=EmailConfirmationResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя с отправкой кода подтверждения"""
    try:
        # Создаем пользователя
        db_user = create_user(db, user)
        
        # Отправляем код подтверждения
        try:
            send_verification_code(db, db_user)
            return EmailConfirmationResponse(
                message=f"Пользователь зарегистрирован! Код подтверждения отправлен на {user.email}"
            )
        except Exception as email_error:
            # Если не удалось отправить email, всё равно возвращаем успешный ответ
            return EmailConfirmationResponse(
                message="Пользователь зарегистрирован! Используйте /auth/resend-confirmation для отправки кода."
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании пользователя"
        )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Авторизация пользователя"""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/confirm-email", response_model=EmailConfirmationResponse)
async def confirm_email(confirmation: EmailConfirmation, db: Session = Depends(get_db)):
    """Подтверждение email по коду"""
    try:
        success = verify_email_code(db, confirmation.email, confirmation.code)
        if success:
            return EmailConfirmationResponse(
                message="Email успешно подтвержден! Добро пожаловать в Fluxo!",
                email_confirmed=True
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при подтверждении email"
        )


@router.post("/resend-confirmation", response_model=EmailConfirmationResponse)
async def resend_confirmation(request: EmailConfirmationRequest, db: Session = Depends(get_db)):
    """Повторная отправка кода подтверждения"""
    # Находим пользователя
    user = get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким email не найден"
        )
    
    # Проверяем, не подтвержден ли уже email
    if user.is_email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже подтвержден"
        )
    
    try:
        # Отправляем новый код
        send_verification_code(db, user)
        return EmailConfirmationResponse(
            message="Код подтверждения отправлен на ваш email"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при отправке кода подтверждения"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    """Получение текущего пользователя по JWT токену"""
    token = credentials.credentials
    email = verify_token(token)
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user


@router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Смена пароля пользователя"""
    # Получаем полную модель пользователя из БД
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    try:
        # Меняем пароль
        change_user_password(
            db=db,
            user=user,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        return PasswordChangeResponse(message="Пароль успешно изменен")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при смене пароля"
        )