from django.core.management.base import BaseCommand
from parser.models import City
from parser.constants import MILLION_CITIES


class Command(BaseCommand):
    help = "Заполняет поле population в City из словаря MILLION_CITIES"

    def handle(self, *args, **kwargs):
        updated = 0

        for city_name, population in MILLION_CITIES.items():
            updated += City.objects.filter(name=city_name).update(population=population)

        self.stdout.write(self.style.SUCCESS(f"✅ Population обновлено для {updated} городов!"))
