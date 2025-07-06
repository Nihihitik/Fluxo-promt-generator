import os
import random
import string
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.user import User
from models.email_verification import EmailVerificationCode
from schemas.user import UserCreate
from services.email_service import send_verification_email, send_welcome_email

# Настройка логирования
logger = logging.getLogger(__name__)

# Конфигурация для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Конфигурация JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширует пароль"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создает JWT токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Проверяет JWT токен и возвращает email пользователя"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Получает пользователя по email"""
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Аутентифицирует пользователя"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_user(db: Session, user: UserCreate) -> User:
    """Создает нового пользователя"""
    # Проверяем, что пользователь с таким email не существует
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    # Хешируем пароль
    hashed_password = get_password_hash(user.password)

    # Создаем пользователя
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        name=user.name
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def change_user_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
    """Изменяет пароль пользователя"""
    # Проверяем текущий пароль
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль"
        )
    
    # Проверяем, что новый пароль отличается от текущего
    if verify_password(new_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новый пароль должен отличаться от текущего"
        )
    
    # Хешируем новый пароль
    new_password_hash = get_password_hash(new_password)
    
    # Обновляем пароль
    user.password_hash = new_password_hash
    db.commit()
    db.refresh(user)
    
    return True

def generate_verification_code() -> str:
    """Генерирует 6-значный код подтверждения"""
    return ''.join(random.choices(string.digits, k=6))

def create_verification_code(db: Session, user: User) -> str:
    """Создает новый код подтверждения для пользователя"""
    # Деактивируем все старые коды
    old_codes = db.query(EmailVerificationCode).filter(
        EmailVerificationCode.user_id == user.id,
        EmailVerificationCode.is_used == False
    ).all()
    
    for code in old_codes:
        code.is_used = True
    
    # Генерируем новый код
    verification_code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=15)  # Код действует 15 минут
    
    # Создаем запись в БД
    db_code = EmailVerificationCode(
        user_id=user.id,
        code=verification_code,
        expires_at=expires_at
    )
    
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    
    return verification_code

def send_verification_code(db: Session, user: User) -> bool:
    """Отправляет код подтверждения пользователю"""
    logger.info(f"🔄 Попытка отправки кода подтверждения для пользователя {user.email}")
    
    # Проверяем лимит отправок (не более 3 в час)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_codes = db.query(EmailVerificationCode).filter(
        EmailVerificationCode.user_id == user.id,
        EmailVerificationCode.created_at > one_hour_ago
    ).count()
    
    logger.info(f"📊 Количество кодов за последний час: {recent_codes}/3")
    
    if recent_codes >= 3:
        logger.warning(f"⚠️ Превышен лимит отправки для пользователя {user.email}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Превышен лимит отправки кодов подтверждения. Попробуйте через час."
        )
    
    # Создаем новый код
    logger.info("🎲 Генерируем новый код подтверждения...")
    verification_code = create_verification_code(db, user)
    logger.info(f"✨ Код создан: {verification_code}")
    
    # Отправляем email
    try:
        logger.info("📧 Начинаем отправку email...")
        success = send_verification_email(user.email, verification_code, user.name)
        
        if not success:
            logger.error("❌ Функция send_verification_email вернула False")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить email с кодом подтверждения. Проверьте настройки email сервиса."
            )
        
        logger.info("✅ Код подтверждения успешно отправлен!")
        return True
        
    except HTTPException:
        # Перебрасываем HTTP исключения как есть
        raise
    except Exception as e:
        logger.error(f"💥 Неожиданная ошибка при отправке кода: {str(e)}")
        logger.error(f"🔍 Тип ошибки: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка отправки email: {str(e)}"
        )

def verify_email_code(db: Session, email: str, code: str) -> bool:
    """Проверяет код подтверждения email"""
    # Находим пользователя
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Если email уже подтвержден
    if user.is_email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже подтвержден"
        )
    
    # Ищем активный код
    verification_code = db.query(EmailVerificationCode).filter(
        EmailVerificationCode.user_id == user.id,
        EmailVerificationCode.code == code,
        EmailVerificationCode.is_used == False,
        EmailVerificationCode.expires_at > datetime.utcnow()
    ).first()
    
    if not verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или истекший код подтверждения"
        )
    
    # Помечаем код как использованный
    verification_code.is_used = True
    
    # Подтверждаем email пользователя
    user.is_email_confirmed = True
    
    db.commit()
    
    # Отправляем приветственное письмо
    try:
        send_welcome_email(user.email, user.name)
    except:
        pass  # Не критично, если приветственное письмо не отправится
    
    return True