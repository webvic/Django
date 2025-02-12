import json
import requests
from django.core.management.base import BaseCommand
from parser.models import Category, Role
from parser import constants  # Импортируем все константы из constants.py

# Функция для загрузки справочника ролей из API HH
def fetch_professional_roles():
    """
    Загружает JSON с профессиональными ролями из API HH.
    Возвращает список категорий (каждая категория содержит список ролей).
    """
    response = requests.get(constants.HH_PROF_ROLES_URL)
    if response.status_code == 200:
        return response.json()["categories"]
    else:
        raise Exception(f"Ошибка загрузки данных: {response.status_code}")

class Command(BaseCommand):
    help = "Импортирует категории и роли из API HH в базу данных, если они еще не заполнены."

    def handle(self, *args, **options):
        # Если в таблице Category уже есть записи, считаем, что данные загружены
        if Category.objects.exists():
            self.stdout.write("Данные уже загружены. Пропускаем импорт.")
            return

        try:
            data = fetch_professional_roles()
        except Exception as e:
            self.stderr.write(str(e))
            return

        # Перебираем категории из JSON
        for category_data in data:
            # Предположим, что JSON для категории имеет ключи "id", "name" и "roles"
            # Если ты хочешь использовать внешний идентификатор из HH, можно сохранить его как hh_id
            category_obj = Category.objects.create(
                id=category_data["id"],       # Если у модели настроено переопределение pk, иначе можно использовать: hh_id=category_data["id"]
                name=category_data["name"],
                hh_id=category_data["id"]
            )

            # Перебираем роли в категории
            for role_data in category_data.get("roles", []):
                Role.objects.create(
                    id=role_data["id"],         # Аналогично, если модель позволяет задавать pk вручную
                    name=role_data["name"],
                    hh_id=role_data["id"],
                    category=category_obj       # Это поле ForeignKey — в БД оно отразится как category_id
                )

        self.stdout.write("✅ Роли и категории успешно загружены в базу.")
