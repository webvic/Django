from django.core.management.base import BaseCommand
import sqlite3
from parser.models import Category, Role, City, Vacancy, KeySkill

class Command(BaseCommand):
    help = 'Переносит данные из старой SQLite-базы (со схожими моделями) в новое Django-приложение.'

    def handle(self, *args, **options):
        old_db_path = 'hh-vacancies.db'
        self.stdout.write(self.style.WARNING('Подключаемся к старой базе: ' + old_db_path))

        conn = sqlite3.connect(old_db_path)
        cursor = conn.cursor()

        # ----------------
        # 1. Перенос категорий
        # ----------------
        categories_map = {}
        cursor.execute("SELECT id, name FROM categories")
        for old_id, name in cursor.fetchall():
            cat = Category.objects.create(
                name=name,
                id_cian=old_id  # <-- Сохраняем старый ID в поле id_cian
            )
            categories_map[old_id] = cat

        # ----------------
        # 2. Перенос ролей
        # ----------------
        roles_map = {}
        cursor.execute("SELECT id, name, category_id FROM roles")
        for old_id, name, old_cat_id in cursor.fetchall():
            category_obj = categories_map.get(old_cat_id)
            role = Role.objects.create(
                name=name,
                category=category_obj,
                id_cian=old_id  # <-- Старый ID
            )
            roles_map[old_id] = role

        # ----------------
        # 3. Города
        # ----------------
        cities_map = {}
        cursor.execute("SELECT id, name, parent_id FROM cities")
        city_rows = cursor.fetchall()
        for old_id, name, parent_id in city_rows:
            city_obj = City.objects.create(
                name=name,
                id_cian=old_id  # <-- Старый ID
            )
            cities_map[old_id] = city_obj

        # Привязываем parent
        for old_id, name, parent_id in city_rows:
            if parent_id and parent_id in cities_map:
                city_obj = cities_map[old_id]
                parent_obj = cities_map[parent_id]
                city_obj.parent = parent_obj
                city_obj.save()

        # ----------------
        # 4. Ключевые навыки (пример без id_cian)
        # ----------------
        skills_map = {}
        cursor.execute("SELECT id, skill_name FROM key_skills")
        for old_id, skill_name in cursor.fetchall():
            skill_obj = KeySkill.objects.create(
                skill_name=skill_name
                # Если надо, можно добавить id_cian и сюда
            )
            skills_map[old_id] = skill_obj

        # ----------------
        # 5. Вакансии
        # ----------------
        vacancies_map = {}
        cursor.execute("SELECT id, vacancy_name, date_time, salary_from, salary_to FROM vacancies")
        for old_id, vacancy_name, date_time, salary_from, salary_to in cursor.fetchall():
            vac = Vacancy.objects.create(
                vacancy_name=vacancy_name,
                date_time=date_time,
                salary_from=salary_from,
                salary_to=salary_to,
                id_cian=old_id  # <-- Старый ID
            )
            vacancies_map[old_id] = vac

        # ---------------------------
        # 5.1 Связь Вакансия - Город
        # ---------------------------
        try:
            cursor.execute("SELECT vacancy_id, city_id FROM vacancy_city")
            for v_id, c_id in cursor.fetchall():
                vac_obj = vacancies_map.get(v_id)
                city_obj = cities_map.get(c_id)
                if vac_obj and city_obj:
                    vac_obj.cities.add(city_obj)
        except sqlite3.OperationalError:
            self.stdout.write(self.style.WARNING('Таблица vacancy_city отсутствует, пропускаем...'))

        # ---------------------------
        # 5.2 Связь Вакансия - Роль
        # ---------------------------
        try:
            cursor.execute("SELECT vacancy_id, role_id FROM vacancy_role")
            for v_id, r_id in cursor.fetchall():
                vac_obj = vacancies_map.get(v_id)
                role_obj = roles_map.get(r_id)
                if vac_obj and role_obj:
                    vac_obj.roles.add(role_obj)
        except sqlite3.OperationalError:
            self.stdout.write(self.style.WARNING('Таблица vacancy_role отсутствует, пропускаем...'))

        # ---------------------------
        # 5.3 Связь Вакансия - KeySkill
        # ---------------------------
        try:
            cursor.execute("SELECT vacancy_id, keyskill_id FROM vacancy_keyskill")
            for v_id, k_id in cursor.fetchall():
                vac_obj = vacancies_map.get(v_id)
                skill_obj = skills_map.get(k_id)
                if vac_obj and skill_obj:
                    vac_obj.key_skills.add(skill_obj)
        except sqlite3.OperationalError:
            self.stdout.write(self.style.WARNING('Таблица vacancy_keyskill отсутствует, пропускаем...'))

        # Закрываем соединение
        conn.close()
        self.stdout.write(self.style.SUCCESS('Все данные успешно перенесены, старые ID сохранены в поле id_cian!'))
