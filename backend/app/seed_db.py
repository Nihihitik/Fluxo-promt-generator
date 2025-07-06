#!/usr/bin/env python3
"""
Скрипт для ручного заполнения базы данных начальными данными
Использование: python seed_db.py
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.seed_data import seed_initial_data

if __name__ == "__main__":
    print("🌱 Запуск ручного заполнения базы данных...")
    try:
        seed_initial_data()
        print("✅ Заполнение базы данных завершено успешно!")
    except Exception as e:
        print(f"❌ Ошибка при заполнении базы данных: {e}")
        sys.exit(1)