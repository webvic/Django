
from django.urls import path
from parser import views

app_name = 'parser'

urlpatterns = [
    path('', views.main_view, name='home'),  # Главная страница
    path("form/", views.form_view, name="job_search_form"),  # 🔥 Добавили `name`
    path('results/', views.results, name='results'),  # Добавляем путь для результатов
]

