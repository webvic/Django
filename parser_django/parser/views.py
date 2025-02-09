from django.shortcuts import render
from .models import *
from django.db.models import F, FloatField, ExpressionWrapper, Q, Case, Value, When, IntegerField
from django.db.models.functions import Coalesce
from .constants import *  
from django.http import JsonResponse
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
def form(request):
    """Обрабатывает форму поиска и передаёт данные в шаблон"""
    
    categories = Category.objects.all().order_by("name")  # Берем все объекты категорий
    roles = Role.objects.all()  # Все роли

    population_case = Case(
        *[When(name=city, then=Value(pop)) for city, pop in MILLION_CITIES.items()],
        output_field=IntegerField()
    )

    top_cities = (
        City.objects
        .filter(name__in=MILLION_CITIES.keys())
        .annotate(_sort_population=population_case)
        .values("hh_id", "name")
        .order_by("-_sort_population")[:10]
    )

    return render(
        request, "parser/form.html",
        {
            "categories": categories,
            "roles": roles,  # Теперь передаём все роли
            "cities": top_cities,
            "default_category": DEFAULT_CATEGORY_HH_ID,
            "proverb": random.choice(proverbs),  # Передаём пословицу в шаблон
        }
    )

def results(request):
    return render(request, 'parser/results.html', {'message': 'Здесь будут результаты поиска'})

