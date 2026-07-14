from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('',      views.page_chatbot, name='page'),
    path('ajax/', views.ajax_message, name='ajax'),
]