import requests
from django.core.management.base import BaseCommand
from parser.models import Category, Role
from parser import constants  # Импорт всех констант, включая HH_PROF_ROLES_URL

def fetch_professional_roles():
    """Загружает JSON со справочником ролей из API HH."""
    response = requests.get(constants.HH_PROF_ROLES_URL)
    if response.status_code == 200:
        data = response.json()
        
        # Дебаг: Выведем, что приходит
        print("JSON-ответ:", data)

        # Проверяем, является ли data словарем (значит, нам нужен ключ с категориями)
        if isinstance(data, dict):
            if "categories" in data:  # Ищем нужный ключ
                return data["categories"]
            else:
                raise ValueError("Ошибка: в JSON-ответе нет ключа 'categories'")
        
        # Если data уже список, значит все в порядке
        return data
    else:
        raise Exception(f"Ошибка загрузки данных: {response.status_code}")


class Command(BaseCommand):
    help = "Восстанавливает поле category_id для ролей на основе JSON справочника"

    def handle(self, *args, **options):
        self.stdout.write("🔄 Загружаем JSON справочник ролей-категорий...")

        try:
            data = fetch_professional_roles()
        except Exception as e:
            self.stderr.write(f"❌ Ошибка загрузки данных: {e}")
            return

        # Создаем словарь соответствий category_hh_id -> category_id (из БД)
        categories = {cat.hh_id: cat.id for cat in Category.objects.all()}

        # Список обновляемых ролей
        updates = []

        for category in data:
            cat_hh_id = int(category["id"])
            cat_id = int(categories.get(cat_hh_id))  # Получаем внутренний ID категории

            if not cat_id:
                self.stdout.write(f"⚠ Категория {cat_hh_id} отсутствует в БД, пропускаем")
                continue

            for role in category.get("roles", []):
                updates.append((int(role["id"]), cat_id))

        # Обновляем записи разом
        for role_hh_id, cat_id in updates:
            Role.objects.filter(hh_id=role_hh_id).update(category_id=cat_id)

        self.stdout.write(f"✅ Успешно обновлено {len(updates)} записей.")
