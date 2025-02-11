from django import forms
from .models import Role, City, Category

class JobSearchForm(forms.Form):
    queryString = forms.CharField(
        max_length=255,
        label="Название профессии",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "ML"})
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Категория",
        widget=forms.Select(attrs={"class": "form-select", "id": "category"})
    )

    professionalRole = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        label="Профессиональная роль",
        widget=forms.SelectMultiple(attrs={"class": "form-select", "id": "role"})
    )

    areas = forms.ModelMultipleChoiceField(
        queryset=City.objects.filter(population__isnull=False).order_by("-population")[:14],  # 🔥 ТОП-14
        required=False,
        label="Выберите город (без выбора - все)",
        widget=forms.SelectMultiple(attrs={"class": "form-select"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Добавляем `data-category` в роли для фильтрации через JS
        self.fields["professionalRole"].widget.choices = [
            (role.pk, role.name, {"data-category": role.category.pk if role.category else "all"})
            for role in Role.objects.all()
        ]
