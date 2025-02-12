from django.shortcuts import render
from .models import *
from django.db.models import F, FloatField, ExpressionWrapper, Q, Case, Value, When, IntegerField
from django.db.models.functions import Coalesce
from .constants import PROVERBS  
from .forms import JobSearchForm
import random

proverbs = PROVERBS.strip().splitlines()

# Create your views here.
def main_view(request):
    # Выбираем вакансии, где хотя бы одно поле зарплаты указано
    vacancies = Vacancy.objects.filter(
        Q(salary_from__isnull=False) | Q(salary_to__isnull=False)
    ).annotate(
        salary_to_filled=Coalesce('salary_to', F('salary_from')),  # Если salary_to пуст, берем salary_from
        salary_to_thousands=ExpressionWrapper(
            F('salary_to_filled') / 1000,  # Делим на 1000
            output_field=FloatField()
        )
    ).prefetch_related('cities').order_by('?')[:3]  # Загружаем связанные города и берём 3 вакансии

    print([(vacancy.vacancy_name, vacancy.salary_to_filled) for vacancy in vacancies])
    return render(request, 'parser/index.html', {'vacancies': vacancies})

# Форма поиска
def form_view(request):
    """Обрабатывает форму поиска и передаёт данные в шаблон"""
    form = JobSearchForm(request.POST or None)
    
    # Выбираем случайную цитату
    random_proverb = random.choice(proverbs)

    return render(
        request, "parser/form.html",
        {
            "form": form,  # 🔥 Передаём форму в шаблон
            "proverb": random_proverb,  # 🔥 Передаём цитату в шаблон
        }
    )

def results(request):
    return render(request, 'parser/results.html', {'message': 'Здесь будут результаты поиска'})

