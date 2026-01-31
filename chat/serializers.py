from rest_framework import serializers
from .models import Chat, Message


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_title(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError("Название чата не может быть пустым")
        value = str(value).strip()
        if len(value) > 200:
            raise serializers.ValidationError("Название чата не должно превышать 200 символов")
        return value


class MessageSerializer(serializers.ModelSerializer):
    # Убираем chat из полей ввода - он берется из URL
    chat_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Message
        fields = ['id', 'chat_id', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_text(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError("Текст сообщения не может быть пустым")
        value = str(value).strip()
        if len(value) > 5000:
            raise serializers.ValidationError("Текст сообщения не должен превышать 5000 символов")
        return value


class ChatDetailSerializer(serializers.ModelSerializer):
    # Вместо прямого присвоения messages, используем SerializerMethodField
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'title', 'created_at', 'messages']

    def get_messages(self, obj):
        # Берем limit из контекста (передается из view)
        limit = self.context.get('limit', 20)
        # Получаем сообщения с ограничением
        messages = obj.messages.all()[:limit]
        # Сериализуем их
        return MessageSerializer(messages, many=True).data