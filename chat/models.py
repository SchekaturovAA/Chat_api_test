from django.db import models


class Chat(models.Model):
    # id автоматически создается Django
    title = models.CharField(max_length=200)  # Текст до 200 символов
    created_at = models.DateTimeField(auto_now_add=True)  # Автоматически при создании

    def __str__(self):
        return self.title


class Message(models.Model):
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,  # КАСКАДНОЕ УДАЛЕНИЕ ← ВАЖНО!
        related_name='messages'  # Позволяет обращаться chat.messages.all()
    )
    text = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение в {self.chat.title}"