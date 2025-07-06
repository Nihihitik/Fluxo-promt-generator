from sqlalchemy.orm import Session
from models.prompt_style import PromptStyle
from core.database import SessionLocal


def seed_prompt_styles(db: Session) -> None:
    """Заполняет таблицу prompt_styles начальными данными"""
    
    # Проверяем, есть ли уже данные в таблице
    existing_styles = db.query(PromptStyle).count()
    if existing_styles > 0:
        print(f"📋 Стили промптов уже существуют ({existing_styles} записей), пропускаем инициализацию")
        return
    
    # Создаем базовые стили промптов
    styles_data = [
        {
            "id": 1,
            "name": "Профессиональный",
            "description": "Экспертный подход с точными и компетентными ответами"
        },
        {
            "id": 2,
            "name": "Творческий",
            "description": "Креативный подход с нестандартными решениями"
        },
        {
            "id": 3,
            "name": "Аналитический", 
            "description": "Детальный анализ с разбором по пунктам"
        },
        {
            "id": 4,
            "name": "Простой",
            "description": "Понятные объяснения для новичков с примерами"
        }
    ]
    
    print("🎨 Создание базовых стилей промптов...")
    
    for style_data in styles_data:
        style = PromptStyle(
            id=style_data["id"],
            name=style_data["name"],
            description=style_data["description"]
        )
        db.add(style)
        print(f"  ✅ Добавлен стиль: {style_data['name']} (ID: {style_data['id']})")
    
    try:
        db.commit()
        print("✅ Все стили промптов успешно созданы!")
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при создании стилей: {e}")
        raise


def seed_initial_data() -> None:
    """Заполняет базу данных начальными данными"""
    print("🌱 Запуск инициализации начальных данных...")
    
    db = SessionLocal()
    try:
        seed_prompt_styles(db)
        print("✅ Инициализация данных завершена успешно!")
    except Exception as e:
        print(f"❌ Ошибка при инициализации данных: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Если скрипт запускается напрямую
    seed_initial_data()