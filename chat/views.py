from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer, ChatDetailSerializer


class ChatCreateView(generics.CreateAPIView):
    """Создание нового чата"""
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_201_CREATED
        return response


class MessageCreateView(generics.CreateAPIView):
    """Создание сообщения в чате"""
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        # Добавляем chat_id из URL к данным запроса
        request.data['chat_id'] = kwargs.get('chat_id')
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)
        serializer.save(chat=chat)


class ChatDetailView(generics.RetrieveAPIView):
    """Получение чата с последними сообщениями"""
    queryset = Chat.objects.all()
    serializer_class = ChatDetailSerializer

    def get_serializer_context(self):
        # Передаем limit в контекст сериализатора
        context = super().get_serializer_context()
        try:
            limit = int(self.request.GET.get('limit', 20))
            if limit < 1:
                limit = 20
            if limit > 100:
                limit = 100  # Максимум 100, как указано в задании
        except (ValueError, TypeError):
            limit = 20
        context['limit'] = limit
        return context

    def get_serializer_context(self):
        # Передаем limit в контекст сериализатора
        context = super().get_serializer_context()
        try:
            limit = int(self.request.GET.get('limit', 20))
            if limit < 1 or limit > 100:
                limit = 20
        except (ValueError, TypeError):
            limit = 20
        context['limit'] = limit
        return context


class ChatDeleteView(generics.DestroyAPIView):
    """Удаление чата со всеми сообщениями"""
    queryset = Chat.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)