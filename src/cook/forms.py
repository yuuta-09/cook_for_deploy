from django import forms
from django.forms import ModelForm

from .models import Recipe, Ingredient
from .redis_utils import RedisHandler


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description']
        labels = {
            'name': '料理名',
            'description': '詳細(作り方等)'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'off'
            }),
            'description': forms.Textarea(attrs={
                'cols': 30,
                'rows': 10,
                'class': 'form-control'
            })
        }


class IngredientForm(ModelForm):
    max_form_num = 10
    min_form_num = 3
    default_form_num = 3
    redis_handler = RedisHandler()

    class Meta:
        model = Ingredient
        fields = ['name', 'amount']
        labels = {
            'name': '材料名',
            'amount': '量'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.TextInput(attrs={'class': 'form-control'})
        }

    def is_form_num_in_range(self, form_num):
        return self.min_form_num <= form_num <= self.max_form_num

    def get_num_of_forms(self, user_id):
        try:
            form_num = self.redis_handler.get_value_from_key(
                f'form_count_{user_id}'
            )
        except KeyError:
            self.set_num_of_forms(user_id, self.default_form_num)
            form_num = self.default_form_num

        return int(form_num)

    def set_num_of_forms(self, user_id, count):
        self.redis_handler.set_key_and_value(f'form_count_{user_id}', count)
