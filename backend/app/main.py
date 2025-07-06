import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, prompts
from core.database import create_tables

app = FastAPI(title="Fluxo API", version="1.0.0")

# Создаем таблицы при запуске приложения
@app.on_event("startup")
async def startup_event():
    print("🚀 Запуск приложения Fluxo API...")
    try:
        create_tables()
        print("✅ Инициализация базы данных завершена успешно!")
        
        # Дополнительная проверка и инициализация данных
        from core.seed_data import seed_initial_data
        seed_initial_data()
        
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        # Не останавливаем приложение, чтобы можно было диагностировать проблемы
        pass

# Настройка CORS
origins = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",  # Alternative localhost
]

# Добавляем дополнительные origins из переменной окружения, если они есть
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
if cors_origins and cors_origins[0]:  # Проверяем, что не пустой список
    origins.extend([origin.strip() for origin in cors_origins])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(prompts.router)

@app.get('/health')
def check_health():
    return {'status': 'ok'}
