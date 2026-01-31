'''
API для чатов и сообщений
Простой REST API для управления чатами и сообщениями на Django. Этот проект был создан как тестовое задание для позиции Junior Python Backend Developer.

Что умеет этот проект - 
1.Создавать новые чаты

2.Отправлять сообщения в чаты

3.Получать чат с последними сообщениями

4.Удалять чаты (сообщения удаляются автоматически)

5.Проверять данные на правильность (например, не пустые сообщения)

6.Работает в Docker контейнерах

Как запустить проект - 

1.Установите Docker и Docker Compose.

2.Скачайте проект: 

git clone https://github.com/ваш-логин/chats-api.git
cd chats-api

3.Запустите одной командой:

docker-compose up --build

4.Откройте в браузере:

API: http://localhost:8000/api/chats/

Админка: http://localhost:8000/admin/

Как пользоваться API - 

1.Создать чат: 

POST http://localhost:8000/api/chats/
{
    "title": "Название чата"
}

2.Отправить сообщение:

POST http://localhost:8000/api/chats/1/messages/
{
    "text": "Текст сообщения"
}

3.Получить чат с сообщениями:

GET http://localhost:8000/api/chats/1/?limit=10
limit - сколько сообщений показать (от 1 до 100, по умолчанию 20)

4.Удалить чат:

DELETE http://localhost:8000/api/chats/1/delete/

Полная проверка API - 

python check_api.py

Технологический стек

Backend: Django 4.2 + Django REST Framework

База данных: PostgreSQL 17

Контейнеризация: Docker + Docker Compose

Язык: Python 3.12



'''