#!/usr/bin/env python3
"""
Скрипт для запуска автотестов
Используется для проверки выполнения заданий
"""

import sys
import os
import subprocess


def run_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("ЗАПУСК АВТОТЕСТОВ ДЛЯ ПРОВЕРКИ ЗАДАНИЙ")
    print("=" * 60)

    # Проверяем наличие pytest
    try:
        import pytest

        print("✓ pytest найден")
    except ImportError:
        print("✗ pytest не найден. Установите: pip install pytest pytest-cov")
        return False

    # Список тестовых файлов
    test_files = [
        "tests/test_models.py",
        "tests/test_controllers.py",
        "tests/test_database.py",
    ]

    # Проверяем наличие тестовых файлов
    missing_files = []
    for test_file in test_files:
        if not os.path.exists(test_file):
            missing_files.append(test_file)

    if missing_files:
        print("✗ Отсутствуют тестовые файлы:")
        for file in missing_files:
            print(f"  - {file}")
        return False

    print("✓ Все тестовые файлы найдены")

    # Запускаем тесты
    print("\n" + "=" * 60)
    print("ЗАПУСК ТЕСТОВ МОДЕЛЕЙ")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_models.py", "-v"],
            capture_output=True,
            text=True,
        )

        print(result.stdout)
        if result.stderr:
            print("Ошибки:", result.stderr)

    except Exception as e:
        print(f"Ошибка запуска тестов моделей: {e}")

    print("\n" + "=" * 60)
    print("ЗАПУСК ТЕСТОВ КОНТРОЛЛЕРОВ")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_controllers.py", "-v"],
            capture_output=True,
            text=True,
        )

        print(result.stdout)
        if result.stderr:
            print("Ошибки:", result.stderr)

    except Exception as e:
        print(f"Ошибка запуска тестов: {e}")

    print("\n" + "=" * 60)
    print("ЗАПУСК ТЕСТОВ БАЗЫ ДАННЫХ")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_database.py", "-v"],
            capture_output=True,
            text=True,
        )

        print(result.stdout)
        if result.stderr:
            print("Ошибки:", result.stderr)

    except Exception as e:
        print(f"Ошибка запуска тестов: {e}")

    print("\n" + "=" * 60)
    print("ЗАПУСК ВСЕХ ТЕСТОВ С ПОКРЫТИЕМ")
    print("=" * 60)

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--cov=.",
                "--cov-report=term-missing",
            ],
            capture_output=True,
            text=True,
        )

        print(result.stdout)
        if result.stderr:
            print("Ошибки:", result.stderr)

    except Exception as e:
        print(f"Ошибка запуска тестов с покрытием: {e}")

    print("\n" + "=" * 60)
    print("ИНСТРУКЦИИ ПО ЗАПУСКУ")
    print("=" * 60)
    print("Для запуска всех тестов: pytest -v")
    print("Для запуска с покрытием: pytest -v --cov=. --cov-report=html")
    print("Для запуска конкретных тестов:")
    print("  pytest -v tests/test_models.py")
    print("  pytest -v tests/test_controllers.py")
    print("  pytest -v tests/test_database.py")

    return True


if __name__ == "__main__":
    run_tests()
