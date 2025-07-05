from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="Fluxo API", version="1.0.0")

# Подключение роутеров
app.include_router(auth.router)

@app.get('/health')
def check_health():
    return {'status': 'ok'}
