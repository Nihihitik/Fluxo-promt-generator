import os
import logging
import resend
from fastapi import HTTPException, status

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_verification_email(email: str, verification_code: str, user_name: str = None) -> bool:
    """Отправляет email с кодом подтверждения через Resend API"""
    
    logger.info(f"🚀 Начинаем отправку кода подтверждения на {email}")
    logger.info(f"📧 Код подтверждения: {verification_code}")
    
    # Проверяем режим разработки
    environment = os.getenv("ENVIRONMENT", "production")
    logger.info(f"🏗️ Режим работы: {environment}")
    
    # Получаем API ключ из переменной окружения
    api_key = os.getenv("RESEND_API_KEY")
    logger.info(f"🔑 API ключ найден: {'Да' if api_key else 'Нет'}")
    
    if not api_key:
        logger.error("❌ RESEND_API_KEY не найден в переменных окружения")
        
        # В режиме разработки логируем код вместо отправки email
        if environment == "development":
            logger.warning("🔧 РЕЖИМ РАЗРАБОТКИ: код не отправлен, но доступен в логах")
            logger.warning("="*50)
            logger.warning(f"👤 Пользователь: {user_name or 'пользователь'}")
            logger.warning(f"📧 Email: {email}")
            logger.warning(f"🔢 КОД ПОДТВЕРЖДЕНИЯ: {verification_code}")
            logger.warning("="*50)
            return True
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email сервис не настроен - отсутствует RESEND_API_KEY"
        )
    
    # Настраиваем Resend API
    resend.api_key = api_key
    logger.info("⚙️ Resend API настроен")
    
    # Формируем имя пользователя
    name = user_name if user_name else "пользователь"
    logger.info(f"👤 Отправляем письмо пользователю: {name}")
    
    # HTML шаблон для email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Подтверждение email - Fluxo</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .code-container {{
                background: white;
                border: 2px dashed #667eea;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
            }}
            .code {{
                font-size: 32px;
                font-weight: bold;
                color: #667eea;
                letter-spacing: 5px;
            }}
            .footer {{
                color: #666;
                font-size: 14px;
                text-align: center;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Добро пожаловать в Fluxo!</h1>
        </div>
        <div class="content">
            <h2>Привет, {name}!</h2>
            <p>Спасибо за регистрацию в Fluxo - платформе для создания умных промптов!</p>
            
            <p>Для завершения регистрации введите код подтверждения:</p>
            
            <div class="code-container">
                <div class="code">{verification_code}</div>
            </div>
            
            <p><strong>Важно:</strong> Код действителен в течение 15 минут.</p>
            
            <p>Если вы не регистрировались на нашей платформе, просто проигнорируйте это письмо.</p>
        </div>
        <div class="footer">
            <p>С уважением,<br>Команда Fluxo</p>
            <p>Это автоматическое письмо, не отвечайте на него.</p>
        </div>
    </body>
    </html>
    """
    
    try:
        logger.info("📤 Начинаем отправку через Resend API...")
        
        email_data = {
            "from": "Fluxo <onboarding@resend.dev>",
            "to": [email],
            "subject": "Подтверждение email - Fluxo",
            "html": html_content
        }
        
        logger.info(f"📋 Данные для отправки: from={email_data['from']}, to={email_data['to']}, subject={email_data['subject']}")
        
        # Отправляем email через Resend
        response = resend.Emails.send(email_data)
        
        logger.info(f"✅ Email успешно отправлен! Response: {response}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки email: {str(e)}")
        logger.error(f"🔍 Тип ошибки: {type(e).__name__}")
        
        # Логируем дополнительную информацию об ошибке
        if hasattr(e, 'response'):
            logger.error(f"📡 HTTP Response: {e.response}")
        if hasattr(e, 'status_code'):
            logger.error(f"📊 Status Code: {e.status_code}")
            
        return False


def send_welcome_email(email: str, user_name: str = None) -> bool:
    """Отправляет приветственное письмо после подтверждения email"""
    
    logger.info(f"🎉 Отправляем приветственное письмо на {email}")
    
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        logger.error("❌ RESEND_API_KEY не найден для приветственного письма")
        return False
    
    resend.api_key = api_key
    name = user_name if user_name else "пользователь"
    logger.info(f"👋 Приветствуем пользователя: {name}")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Добро пожаловать в Fluxo!</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 10px;
                margin-top: 20px;
            }}
            .button {{
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎉 Email успешно подтвержден!</h1>
        </div>
        <div class="content">
            <h2>Поздравляем, {name}!</h2>
            <p>Ваш email успешно подтвержден. Теперь вы можете пользоваться всеми возможностями Fluxo:</p>
            
            <ul>
                <li>🤖 Создание умных промптов с ИИ</li>
                <li>🎨 Выбор из 4 стилей генерации</li>
                <li>📊 Отслеживание истории запросов</li>
                <li>⚡ Быстрая и качественная обработка</li>
            </ul>
            
            <p>Начните создавать свои первые промпты прямо сейчас!</p>
            
            <p>С уважением,<br>Команда Fluxo</p>
        </div>
    </body>
    </html>
    """
    
    try:
        logger.info("📤 Отправляем приветственное письмо...")
        
        welcome_data = {
            "from": "Fluxo <onboarding@resend.dev>",
            "to": [email],
            "subject": "🎉 Добро пожаловать в Fluxo!",
            "html": html_content
        }
        
        response = resend.Emails.send(welcome_data)
        logger.info(f"✅ Приветственное письмо отправлено! Response: {response}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки приветственного email: {str(e)}")
        return False