import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Конфигурация базы данных
DATABASE_URL = os.getenv("DATABASE_URL")

# Создание движка базы данных
engine = create_engine(DATABASE_URL)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Функция для создания таблиц
def create_tables():
    # Импортируем все модели чтобы они были зарегистрированы в Base.metadata
    from models import (
        Base, 
        User, 
        PromptStyle, 
        PromptRequest, 
        EmailVerificationCode
    )
    
    print("🔧 Создание таблиц в базе данных...")
    print(f"📋 Найдено моделей для создания: {len(Base.metadata.tables)}")
    
    # Выводим список таблиц которые будут созданы
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")
    
    Base.metadata.create_all(bind=engine)
    print("✅ Все таблицы успешно созданы!")