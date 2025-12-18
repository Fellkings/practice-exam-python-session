#!/usr/bin/env python3
"""
Главный файл приложения "Система управления библиотекой"
Запускает GUI приложение с использованием архитектуры MVC
"""

import os
import sys
from tkinter import messagebox

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from controllers.task_controller import TaskController
    from controllers.project_controller import ProjectController
    from controllers.user_controller import UserController
    from database.database_manager import DatabaseManager
    from views.main_window import MainWindow
    from models.task import Task
    from models.project import Project
    from models.user import User
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    print("Убедитесь, что все файлы проекта созданы")
    print("Структура проекта должна содержать:")
    print("  controllers/ - task_controller.py, project_controller.py, user_controller.py")
    print("  views/ - main_window.py")
    print("  models/ - task.py, project.py, user.py")
    print("  database/ - database_manager.py")
    sys.exit(1)

def check_database_connection(db_manager):
    """Проверка подключения к базе данных"""
    try:
        db_manager.create_tables()
        print("База данных успешно подключена")
        return True
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return False


def initialize_models():
    """Инициализация моделей (если требуется)"""
    print("Модели инициализированы:")
    print(f"  - Task: {Task.__name__}")
    print(f"  - Project: {Project.__name__}")
    print(f"  - User: {User.__name__}")


def main():
    """Главная функция приложения"""
    try:
        print("=" * 50)
        print("Запуск системы управления задачами")
        print("=" * 50)
        
        db_path = os.path.join("database", "tasks.db")
        print(f"Используемая база данных: {db_path}")
        
        os.makedirs("database", exist_ok=True)
        
        print("\nЗапуск графического интерфейса...")
        app = MainWindow(db_path)
        
        print("Приложение успешно запущено!")
        print("=" * 50)
        
        app.run()

    except KeyboardInterrupt:
        print("\n\nПриложение остановлено пользователем")
        sys.exit(0)
        
    except Exception as e:
        error_msg = f"Критическая ошибка запуска приложения: {e}"
        print(f"\n❌ {error_msg}")
        messagebox.showerror("Ошибка запуска", error_msg)
        
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
