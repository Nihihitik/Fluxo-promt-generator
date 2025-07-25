# Fluxo - AI-Powered Prompt Generator

**Fluxo** - это PET-проект, представляющий собой полнофункциональный AI-сервис для генерации промптов с системой авторизации и управления пользователями.

## 🚀 Технологический стек

### Backend
- **FastAPI** - современный асинхронный веб-фреймворк с автоматической документацией API
- **PostgreSQL** - база данных для хранения пользователей и запросов
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - система миграций базы данных
- **JWT Authentication** - авторизация на основе токенов
- **OpenRouter API** - интеграция с AI моделями (Mistral AI)
- **Resend** - сервис для отправки email-уведомлений

### Frontend
- **Next.js 15** - React-фреймворк с App Router
- **React 19** - последняя версия React
- **TypeScript** - типизированный JavaScript
- **Tailwind CSS 4** - utility-first CSS фреймворк
- **Radix UI** - компоненты для UI
- **Bun** - пакетный менеджер и сборщик

## 🎯 Основной функционал

### Авторизация и управление пользователями
- Регистрация пользователей с email-подтверждением
- Авторизация через JWT токены
- Верификация email с 6-значными кодами
- Смена пароля для авторизованных пользователей
- Дневные лимиты на запросы (по умолчанию 10 запросов/день)

### Генерация промптов
- 4 предустановленных стиля промптов:
  - **Professional** - экспертные ответы
  - **Creative** - креативные и инновационные подходы
  - **Analytical** - детальный анализ и структура
  - **Simple** - простые объяснения для новичков
- История всех промптов пользователя
- Интеграция с AI моделями через OpenRouter API
- Отслеживание лимитов использования

### Дополнительные возможности
- Профиль пользователя с управлением настройками
- Email-уведомления о важных событиях
- Полная документация API (Swagger UI)
- Обработка ошибок и валидация данных

## 🛠 Установка и запуск

### Предварительные требования
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Bun (для фронтенда)

### Backend

```bash
# Переход в директорию backend
cd backend

# Установка зависимостей
pip install -r app/requirements.txt

# Создание файла окружения
cp .env.example .env
# Настройте переменные окружения в .env файле

# Запуск PostgreSQL (через Docker)
docker-compose up -d

# Создание таблиц базы данных
cd app && python -c "from core.database import create_tables; create_tables()"

# Запуск сервера разработки
cd app && uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
# Переход в директорию frontend
cd frontend

# Установка зависимостей
bun install

# Запуск сервера разработки
bun dev
```

### Доступные URL
- **Backend API**: http://localhost:8000
- **API Документация**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## 🔧 Конфигурация

### Переменные окружения Backend

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fluxo
POSTGRES_DB=fluxo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# JWT Authentication
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenRouter API
OPENROUTER_API_KEY=your-openrouter-key

# Email Service
RESEND_API_KEY=your-resend-key

# CORS Origins (optional)
CORS_ORIGINS=http://localhost:3001,https://yourdomain.com
```

## 📚 API Endpoints

### Авторизация
- `POST /auth/register` - Регистрация нового пользователя
- `POST /auth/login` - Авторизация пользователя
- `GET /auth/me` - Информация о текущем пользователе
- `PUT /auth/change-password` - Смена пароля

### Email-верификация
- `POST /auth/confirm-email` - Подтверждение email кодом
- `POST /auth/resend-confirmation` - Повторная отправка кода

### Генерация промптов
- `POST /prompts/create` - Создание нового промпта
- `GET /prompts/history` - История промптов пользователя
- `GET /prompts/styles` - Доступные стили промптов
- `GET /prompts/limits` - Лимиты пользователя

### Служебные
- `GET /health` - Проверка состояния сервиса
- `GET /docs` - Swagger UI документация
- `GET /redoc` - ReDoc документация

## 🗂 Структура проекта

```
fluxo/
├── backend/
│   ├── app/
│   │   ├── core/           # Основная логика (auth, database, prompt generation)
│   │   ├── models/         # SQLAlchemy модели
│   │   ├── schemas/        # Pydantic схемы
│   │   ├── routers/        # API маршруты
│   │   ├── services/       # Сервисы (email, etc.)
│   │   └── tests/          # Тесты
│   ├── alembic/           # Миграции базы данных
│   └── docker-compose.yaml
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js App Router страницы
│   │   ├── components/    # React компоненты
│   │   ├── context/       # React контексты
│   │   └── lib/           # Утилиты и конфигурация
│   └── public/            # Статические файлы
└── README.md
```

## 🧪 Тестирование

### Backend
```bash
cd backend/app
pytest
```

### Frontend
```bash
cd frontend
bun lint
bun run build  # Включает проверку TypeScript
```

## 🐳 Docker

```bash
# Запуск всего стека
cd backend
docker-compose up -d

# Просмотр логов
docker-compose logs -f fastapi
docker-compose logs -f postgres

# Остановка
docker-compose down
```

## 🔒 Безопасность

- Пароли хешируются с использованием bcrypt
- JWT токены для авторизации
- Валидация всех входящих данных
- CORS настройки для безопасности
- Переменные окружения для секретных данных

## 📄 Лицензия

Этот проект является PET-проектом, созданным в образовательных целях.

## 🤝 Контакты

Для вопросов и предложений по проекту создайте issue в репозитории.
