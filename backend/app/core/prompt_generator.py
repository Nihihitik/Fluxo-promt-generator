import os
import httpx
from typing import Optional
from fastapi import HTTPException, status


async def generate_prompt(original_prompt: str, style_id: Optional[int]) -> str:
    """Генерирует промпт на основе исходного текста и стиля через OpenRouter API"""
    
    # Если стиль не указан, генерируем базовый промпт
    if not style_id:
        return await call_openrouter_api(original_prompt)
    
    # Применяем стиль к промпту
    styled_prompt = apply_style(original_prompt, style_id)
    
    # Генерируем ответ через OpenRouter API
    return await call_openrouter_api(styled_prompt)


def apply_style(prompt: str, style_id: int) -> str:
    """Применяет стиль к промпту на основе ID"""
    
    style_templates = {
        1: f"Ты профессиональный эксперт в данной области. Дай точный и компетентный ответ на следующий вопрос: {prompt}",
        2: f"Подойди к этому вопросу творчески и нестандартно. Предложи оригинальные идеи и решения: {prompt}",
        3: f"Проанализируй этот вопрос детально и структурированно. Разбери по пунктам и дай всесторонний анализ: {prompt}",
        4: f"Объясни это простым и понятным языком для новичка. Используй примеры и аналогии: {prompt}"
    }
    
    # Получаем шаблон для стиля или возвращаем исходный промпт
    return style_templates.get(style_id, prompt)


async def call_openrouter_api(prompt: str) -> str:
    """Вызывает OpenRouter API для генерации ответа"""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenRouter API key не настроен"
        )
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://fluxo.app",
        "X-Title": "Fluxo"
    }
    
    payload = {
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Ошибка OpenRouter API: {response.status_code}"
                )
            
            data = response.json()
            
            if "choices" not in data or not data["choices"]:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Пустой ответ от OpenRouter API"
                )
            
            return data["choices"][0]["message"]["content"]
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Таймаут запроса к OpenRouter API"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка соединения с OpenRouter API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка при обращении к API: {str(e)}"
        )


def get_available_styles() -> dict:
    """Возвращает доступные стили промптов"""
    return {
        1: {
            "name": "Профессиональный",
            "description": "Экспертный подход с точными и компетентными ответами"
        },
        2: {
            "name": "Творческий", 
            "description": "Креативный подход с нестандартными решениями"
        },
        3: {
            "name": "Аналитический",
            "description": "Детальный анализ с разбором по пунктам"
        },
        4: {
            "name": "Простой",
            "description": "Понятные объяснения для новичков с примерами"
        }
    }