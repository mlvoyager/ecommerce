from django.urls import path
from chatbot import views

urlpatterns = [
    path('repondre/', views.repondre, name='repondre'),
]