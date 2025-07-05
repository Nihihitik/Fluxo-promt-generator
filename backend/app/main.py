import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, prompts

app = FastAPI(title="Fluxo API", version="1.0.0")

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
