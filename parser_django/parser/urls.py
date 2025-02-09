
from django.urls import path
from parser import views

app_name = 'parser'

urlpatterns = [
    path('', views.main_view, name='home'),  # Главная страница
    path('form/', views.form, name='form'),  # Добавляем путь к форме
    path('results/', views.results, name='results'),  # Добавляем путь для результатов
]

