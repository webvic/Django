from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # Новое поле:
    id_cian = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='roles')
    # Новое поле:
    id_cian = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="subcities")
    # Новое поле:
    id_cian = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    vacancy_name = models.CharField(max_length=255)
    date_time = models.IntegerField()
    salary_from = models.FloatField(null=True, blank=True)
    salary_to = models.FloatField(null=True, blank=True)

    # Новое поле:
    id_cian = models.IntegerField(unique=True)

    # M2M-поля
    cities = models.ManyToManyField(City, related_name='vacancies')
    roles = models.ManyToManyField(Role, related_name='vacancies')
    key_skills = models.ManyToManyField('KeySkill', related_name='vacancies')

    def __str__(self):
        return self.vacancy_name

# Ключевые навыки
class KeySkill(models.Model):
    skill_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.skill_name

