from django.urls import path
from . import views

app_name = 'cook'
urlpatterns = [
    # レシピ
    path(
        'recipes/',
        views.RecipeListView.as_view(),
        name='recipe_list'
    ),
    path(
        'recipes/<int:recipe_id>/',
        views.RecipeDetailView.as_view(),
        name='recipe_detail'
    ),
    path(
        'recipes/new/',
        views.RecipeCreateView.as_view(),
        name='recipe_new'
    ),
    path(
        'recipes/<int:recipe_id>/edit/',
        views.RecipeUpdateView.as_view(),
        name='recipe_edit'
    ),
    path(
        'recipes/<int:recipe_id>/destroy/',
        views.RecipeDeleteView.as_view(),
        name='recipe_destroy'
    ),
    # 具材
    path(
        'recipes/<int:recipe_id>/ingredients/new/',
        views.IngredientCrateView.as_view(),
        name='ingredient_new'
    ),
    path(
        'recipes/ingredients/<int:ingredient_id>/edit/',
        views.IngredientUpdateView.as_view(),
        name='ingredient_edit'
    ),
    path(
        'ingredients/<int:ingredient_id>/destroy',
        views.IngredientDeleteView.as_view(),
        name='ingredient_destroy'
    ),
]
