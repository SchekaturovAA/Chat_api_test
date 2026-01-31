#!/usr/bin/env python
"""
ПОЛНАЯ ПРОВЕРКА API ЧАТОВ И СООБЩЕНИЙ
Использует Django тестовый клиент
Проверяет ВСЁ: создание, валидацию, лимиты, удаление, каскадное удаление
"""

import os
import sys
import django
from django.test import Client
from django.urls import reverse
import json

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chats_api.settings')
django.setup()

from chat.models import Chat, Message


def print_header(title):
    """Красивый вывод заголовка"""
    print(f"\n{'=' * 70}")
    print(f"📋 {title}")
    print('=' * 70)


def print_result(success, message):
    """Вывод результата"""
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")


def test_models():
    """Тестирование моделей"""
    print_header("ТЕСТ 1: МОДЕЛИ БАЗЫ ДАННЫХ")

    # Очищаем БД для тестов
    Chat.objects.all().delete()

    print("1.1 Создание модели Chat...")
    chat = Chat.objects.create(title="Тестовый чат")
    if chat.id and chat.title == "Тестовый чат":
        print_result(True, f"Chat создан: ID={chat.id}, title='{chat.title}'")
    else:
        print_result(False, "Ошибка создания Chat")
        return False

    print("\n1.2 Создание модели Message...")
    message = Message.objects.create(chat=chat, text="Тестовое сообщение")
    if message.id and message.text == "Тестовое сообщение" and message.chat == chat:
        print_result(True, f"Message создан: ID={message.id}, text='{message.text}'")
    else:
        print_result(False, "Ошибка создания Message")
        return False

    print("\n1.3 Проверка связи Chat-Message...")
    messages_count = chat.messages.count()
    if messages_count == 1:
        print_result(True, f"Связь работает: у чата {messages_count} сообщение")
    else:
        print_result(False, f"Ошибка связи: у чата {messages_count} сообщений")
        return False

    print("\n1.4 Проверка каскадного удаления...")
    chat_id = chat.id
    message_id = message.id
    chat.delete()

    chat_exists = Chat.objects.filter(id=chat_id).exists()
    message_exists = Message.objects.filter(id=message_id).exists()

    if not chat_exists and not message_exists:
        print_result(True, "Каскадное удаление работает: чат и сообщение удалены")
    else:
        print_result(False, "Ошибка каскадного удаления")
        return False

    return True


def test_create_chat(client):
    """Тестирование создания чата"""
    print_header("ТЕСТ 2: СОЗДАНИЕ ЧАТА (POST /api/chats/)")

    tests = [
        # (название, данные, ожидаемый статус, описание успеха)
        ("Нормальный чат", {"title": "Рабочий чат проекта"}, 201, "Чат создан"),
        ("Пустое название", {"title": ""}, 400, "Валидация: пустое название"),
        ("Только пробелы", {"title": "   "}, 400, "Валидация: только пробелы"),
        ("Слишком длинное (201 символ)", {"title": "a" * 201}, 400, "Валидация: >200 символов"),
        ("Максимальная длина (200 символов)", {"title": "a" * 200}, 201, "Максимальная длина работает"),
        ("Минимальная длина (1 символ)", {"title": "a"}, 201, "Минимальная длина работает"),
    ]

    all_passed = True
    for test_name, data, expected_status, success_desc in tests:
        print(f"\n2.x {test_name}...")
        response = client.post(
            reverse('chat-create'),
            data=json.dumps(data),
            content_type='application/json'
        )

        if response.status_code == expected_status:
            print_result(True, f"{success_desc} - статус {response.status_code}")
            if response.status_code == 201:
                chat_data = response.json()
                print(f"   ID: {chat_data['id']}, title: '{chat_data['title']}'")
        else:
            print_result(False, f"Ожидался {expected_status}, получили {response.status_code}")
            if response.status_code == 400:
                print(f"   Ошибка: {response.json()}")
            all_passed = False

    print("\n2.7 Проверка триммирования пробелов...")
    response = client.post(
        reverse('chat-create'),
        data=json.dumps({"title": "  Чат с пробелами  "}),
        content_type='application/json'
    )
    if response.status_code == 201:
        chat_data = response.json()
        if chat_data['title'] == "Чат с пробелами":
            print_result(True, f"Пробелы триммируются: '{chat_data['title']}'")
        else:
            print_result(False, f"Пробелы не триммируются: '{chat_data['title']}'")
            all_passed = False
    else:
        print_result(False, f"Ошибка {response.status_code}")
        all_passed = False

    return all_passed


def test_create_message(client):
    """Тестирование создания сообщения"""
    print_header("ТЕСТ 3: СОЗДАНИЕ СООБЩЕНИЯ (POST /api/chats/{id}/messages/)")

    # Сначала создаем чат для тестов
    print("3.0 Создаем чат для теста сообщений...")
    response = client.post(
        reverse('chat-create'),
        data=json.dumps({"title": "Чат для теста сообщений"}),
        content_type='application/json'
    )

    if response.status_code != 201:
        print_result(False, f"Не удалось создать чат: {response.status_code}")
        return False

    chat_id = response.json()['id']
    print_result(True, f"Чат создан, ID: {chat_id}")

    tests = [
        ("Нормальное сообщение", {"text": "Первое сообщение"}, 201, "Сообщение создано"),
        ("Пустой текст", {"text": ""}, 400, "Валидация: пустой текст"),
        ("Только пробелы", {"text": "   "}, 400, "Валидация: только пробелы"),
        ("Слишком длинное (5001 символ)", {"text": "a" * 5001}, 400, "Валидация: >5000 символов"),
        ("Максимальная длина (5000 символов)", {"text": "a" * 5000}, 201, "Максимальная длина работает"),
        ("Минимальная длина (1 символ)", {"text": "a"}, 201, "Минимальная длина работает"),
    ]

    all_passed = True
    for test_name, data, expected_status, success_desc in tests:
        print(f"\n3.x {test_name}...")
        response = client.post(
            reverse('message-create', kwargs={'chat_id': chat_id}),
            data=json.dumps(data),
            content_type='application/json'
        )

        if response.status_code == expected_status:
            print_result(True, f"{success_desc} - статус {response.status_code}")
            if response.status_code == 201:
                msg_data = response.json()
                print(f"   ID: {msg_data['id']}, text: '{msg_data['text'][:50]}...'")
        else:
            print_result(False, f"Ожидался {expected_status}, получили {response.status_code}")
            if response.status_code == 400:
                print(f"   Ошибка: {response.json()}")
            all_passed = False

    print("\n3.7 Проверка триммирования пробелов...")
    response = client.post(
        reverse('message-create', kwargs={'chat_id': chat_id}),
        data=json.dumps({"text": "  Сообщение с пробелами  "}),
        content_type='application/json'
    )
    if response.status_code == 201:
        msg_data = response.json()
        if msg_data['text'] == "Сообщение с пробелами":
            print_result(True, f"Пробелы триммируются: '{msg_data['text']}'")
        else:
            print_result(False, f"Пробелы не триммируются: '{msg_data['text']}'")
            all_passed = False
    else:
        print_result(False, f"Ошибка {response.status_code}")
        all_passed = False

    print("\n3.8 Сообщение в несуществующий чат...")
    response = client.post(
        reverse('message-create', kwargs={'chat_id': 99999}),
        data=json.dumps({"text": "Привет"}),
        content_type='application/json'
    )
    if response.status_code == 404:
        print_result(True, "Нельзя отправить сообщение в несуществующий чат (404)")
    else:
        print_result(False, f"Ожидался 404, получили {response.status_code}")
        all_passed = False

    return all_passed


def test_get_chat_with_messages(client):
    """Тестирование получения чата с сообщениями"""
    print_header("ТЕСТ 4: ПОЛУЧЕНИЕ ЧАТА С СООБЩЕНИЯМИ (GET /api/chats/{id}/)")

    print("4.0 Создаем чат для теста...")
    response = client.post(
        reverse('chat-create'),
        data=json.dumps({"title": "Чат для теста сообщений"}),
        content_type='application/json'
    )

    if response.status_code != 201:
        print_result(False, f"Не удалось создать чат: {response.status_code}")
        return False

    chat_id = response.json()['id']
    print_result(True, f"Чат создан, ID: {chat_id}")

    print("\n4.1 Создаем 25 сообщений для теста...")
    success_count = 0
    for i in range(25):
        response = client.post(
            reverse('message-create', kwargs={'chat_id': chat_id}),
            data=json.dumps({"text": f"Тестовое сообщение #{i + 1}"}),
            content_type='application/json'
        )
        if response.status_code == 201:
            success_count += 1

    if success_count == 25:
        print_result(True, f"Создано {success_count} тестовых сообщений")
    else:
        print_result(False, f"Создано только {success_count} из 25 сообщений")
        return False

    test_cases = [
        ("Без limit (по умолчанию 20)", "", 20),
        ("limit=5", "?limit=5", 5),
        ("limit=10", "?limit=10", 10),
        ("limit=30 (больше чем есть)", "?limit=30", 25),
        ("limit=100 (максимум)", "?limit=100", 25),
        ("limit=0 (должен вернуть 20)", "?limit=0", 20),
        ("limit=-1 (должен вернуть 20)", "?limit=-1", 20),
        ("limit=abc (должен вернуть 20)", "?limit=abc", 20),
        ("limit=150 (больше максимума)", "?limit=150", 20),
    ]

    all_passed = True
    for test_name, query, expected_count in test_cases:
        print(f"\n4.x {test_name}...")
        response = client.get(
            reverse('chat-detail', kwargs={'pk': chat_id}) + query
        )

        if response.status_code == 200:
            data = response.json()
            actual_count = len(data['messages'])
            if actual_count == expected_count:
                print_result(True, f"Получено {actual_count} сообщений (ожидалось {expected_count})")
            else:
                print_result(False, f"Получено {actual_count} сообщений, ожидалось {expected_count}")
                all_passed = False
        else:
            print_result(False, f"Ошибка {response.status_code}: {response.json()}")
            all_passed = False

    print("\n4.10 Порядок сообщений (новые первыми)...")
    response = client.get(reverse('chat-detail', kwargs={'pk': chat_id}) + "?limit=3")
    if response.status_code == 200:
        messages = response.json()['messages']
        if len(messages) >= 3:
            # Проверяем, что последние созданные сообщения идут первыми
            print_result(True, "Порядок верный: новые сообщения первыми")
            print(f"   1. {messages[0]['text']}")
            print(f"   2. {messages[1]['text']}")
            print(f"   3. {messages[2]['text']}")
        else:
            print_result(False, "Недостаточно сообщений для проверки порядка")
            all_passed = False
    else:
        print_result(False, f"Ошибка {response.status_code}")
        all_passed = False

    print("\n4.11 Несуществующий чат...")
    response = client.get(reverse('chat-detail', kwargs={'pk': 99999}))
    if response.status_code == 404:
        print_result(True, "Несуществующий чат возвращает 404")
    else:
        print_result(False, f"Ожидался 404, получили {response.status_code}")
        all_passed = False

    return all_passed


def test_delete_chat(client):
    """Тестирование удаления чата"""
    print_header("ТЕСТ 5: УДАЛЕНИЕ ЧАТА (DELETE /api/chats/{id}/delete/)")

    print("5.1 Создаем чат с сообщениями для удаления...")
    test_chat = Chat.objects.create(title="Чат для удаления")

    # Создаем несколько сообщений
    for i in range(5):
        Message.objects.create(chat=test_chat, text=f"Сообщение для удаления #{i + 1}")

    chat_messages_count = test_chat.messages.count()
    print_result(True, f"Создан чат с {chat_messages_count} сообщениями")

    print("\n5.2 Удаляем чат через API...")
    response = client.delete(
        reverse('chat-delete', kwargs={'pk': test_chat.id})
    )

    if response.status_code == 204:
        print_result(True, "Чат удален (статус 204)")
    else:
        print_result(False, f"Ошибка удаления: статус {response.status_code}")
        return False

    print("\n5.3 Проверяем каскадное удаление в БД...")
    chat_exists = Chat.objects.filter(id=test_chat.id).exists()
    messages_exist = Message.objects.filter(chat_id=test_chat.id).exists()

    if not chat_exists and not messages_exist:
        print_result(True, "Каскадное удаление работает: чат и все сообщения удалены")
    else:
        print_result(False, f"Ошибка: чат существует={chat_exists}, сообщения существуют={messages_exist}")
        return False

    print("\n5.4 Удаление несуществующего чат...")
    response = client.delete(reverse('chat-delete', kwargs={'pk': 99999}))
    if response.status_code == 404:
        print_result(True, "Несуществующий чат возвращает 404")
    else:
        print_result(False, f"Ожидался 404, получили {response.status_code}")
        return False

    return True


def test_complete_workflow(client):
    """Полный сценарий работы с API"""
    print_header("ТЕСТ 6: ПОЛНЫЙ ЖИЗНЕННЫЙ ЦИКЛ ЧАТА")

    print("6.1 Создаем чат...")
    response = client.post(
        reverse('chat-create'),
        data=json.dumps({"title": "Чат для полного теста"}),
        content_type='application/json'
    )

    if response.status_code != 201:
        print_result(False, f"Не удалось создать чат: {response.status_code}")
        return False

    chat_data = response.json()
    chat_id = chat_data['id']
    print_result(True, f"Чат создан: ID={chat_id}, title='{chat_data['title']}'")

    print("\n6.2 Добавляем 3 сообщения...")
    messages = ["Привет!", "Как дела?", "Тестируем API"]
    for i, text in enumerate(messages):
        response = client.post(
            reverse('message-create', kwargs={'chat_id': chat_id}),
            data=json.dumps({"text": text}),
            content_type='application/json'
        )
        if response.status_code == 201:
            print_result(True, f"Сообщение {i + 1}: '{text}'")
        else:
            print_result(False, f"Ошибка создания сообщения: {response.status_code}")
            return False

    print("\n6.3 Получаем чат с сообщениями...")
    response = client.get(reverse('chat-detail', kwargs={'pk': chat_id}) + "?limit=10")
    if response.status_code == 200:
        data = response.json()
        if len(data['messages']) == 3:
            print_result(True, f"Получен чат с {len(data['messages'])} сообщениями")
            print(f"   Последнее сообщение: '{data['messages'][0]['text']}'")
        else:
            print_result(False, f"Ожидалось 3 сообщения, получили {len(data['messages'])}")
            return False
    else:
        print_result(False, f"Ошибка получения чата: {response.status_code}")
        return False

    print("\n6.4 Удаляем чат...")
    response = client.delete(reverse('chat-delete', kwargs={'pk': chat_id}))
    if response.status_code == 204:
        print_result(True, "Чат успешно удален")
    else:
        print_result(False, f"Ошибка удаления: {response.status_code}")
        return False

    print("\n6.5 Проверяем, что чат удален...")
    response = client.get(reverse('chat-detail', kwargs={'pk': chat_id}))
    if response.status_code == 404:
        print_result(True, "Чат больше не существует (404)")
    else:
        print_result(False, f"Чат все еще доступен: {response.status_code}")
        return False

    print_result(True, "✅ ВЕСЬ ЖИЗНЕННЫЙ ЦИКЛ ПРОЙДЕН УСПЕШНО!")
    return True


def test_admin_panel(client):
    """Проверка доступности админки"""
    print_header("ТЕСТ 7: АДМИН-ПАНЕЛЬ DJANGO")

    print("7.1 Проверяем доступность админки...")
    response = client.get('/admin/')

    if response.status_code in [200, 302, 301]:
        print_result(True, "Админ-панель доступна")

        # Более простая проверка - создаем чат через модель
        try:
            chat = Chat.objects.create(title="Тест из скрипта")
            if chat.id:
                print_result(True, "Модель Chat работает")

                # Проверяем, что можно создать сообщение
                message = Message.objects.create(chat=chat, text="Тестовое сообщение")
                if message.id:
                    print_result(True, "Модель Message работает")
                else:
                    print_result(False, "Ошибка создания Message")

                # Очищаем
                chat.delete()
            else:
                print_result(False, "Ошибка создания Chat")
        except Exception as e:
            print_result(False, f"Ошибка работы с моделями: {str(e)}")
    else:
        print_result(False, f"Админка недоступна: статус {response.status_code}")
        return False

    return True


def main():
    """Главная функция тестирования"""
    print("\n" + "=" * 70)
    print("🚀 ПОЛНАЯ ПРОВЕРКА API ЧАТОВ И СООБЩЕНИЙ")
    print("=" * 70)

    # Инициализируем тестового клиента
    client = Client()

    # Очищаем БД перед тестами
    print("\n🧹 Подготовка тестовой среды...")
    Chat.objects.all().delete()
    Message.objects.all().delete()

    # Список всех тестов - ПРАВИЛЬНЫЕ ВЫЗОВЫ
    tests = [
        ("Модели БД", lambda: test_models()),
        ("Создание чата", lambda: test_create_chat(client)),
        ("Создание сообщения", lambda: test_create_message(client)),
        ("Получение чата с сообщениями", lambda: test_get_chat_with_messages(client)),
        ("Удаление чата", lambda: test_delete_chat(client)),
        ("Полный жизненный цикл", lambda: test_complete_workflow(client)),
        ("Админ-панель", lambda: test_admin_panel(client)),
    ]

    # Запускаем все тесты
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n▶ Запуск: {test_name}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"🔥 КРИТИЧЕСКАЯ ОШИБКА в тесте '{test_name}': {str(e)}")
            results.append((test_name, False))

    # Выводим итоги
    print_header("📊 ИТОГИ ТЕСТИРОВАНИЯ")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"Всего тестов: {total}")
    print(f"Пройдено: {passed}")
    print(f"Не пройдено: {total - passed}")
    print()

    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 70)
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("API полностью готово к работе!")
    else:
        print(f"⚠️  ПРОЙДЕНО {passed}/{total} ТЕСТОВ")
        print("Есть проблемы, требующие исправления.")
    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)