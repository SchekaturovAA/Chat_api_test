from django.urls import path
from . import views

urlpatterns = [
    path('chats/', views.ChatCreateView.as_view(), name='chat-create'),
    path('chats/<int:pk>/', views.ChatDetailView.as_view(), name='chat-detail'),
    path('chats/<int:pk>/delete/', views.ChatDeleteView.as_view(), name='chat-delete'),
    path('chats/<int:chat_id>/messages/', views.MessageCreateView.as_view(), name='message-create'),
]