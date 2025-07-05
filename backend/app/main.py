from fastapi import FastAPI
from routers import auth, prompts

app = FastAPI(title="Fluxo API", version="1.0.0")

# Подключение роутеров
app.include_router(auth.router)
app.include_router(prompts.router)

@app.get('/health')
def check_health():
    return {'status': 'ok'}
