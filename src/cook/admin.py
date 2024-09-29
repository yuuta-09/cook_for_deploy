from django.contrib import admin

from .models import Recipe, Ingredient


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 3


class RecipeAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "posted_at"]
    list_filter = ["posted_at", "user"]
    search_fields = ["name"]
    fieldsets = [
        (
            None,
            {
                'fields': ["name", "description", "posted_at"]
            }
        ),
        (
            "Advanced options",
            {
                "classes": ["collapse"],
                "fields": ["user", "image"]
            }
        )
    ]

    inlines = [IngredientInline]


class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "amount"]
    list_filter = ["recipe"]
    search_fields = ["name"]
    readonly_fields = ("recipe")
    fieldsets = [
        (
            None,
            {
                'fields': ["name", "amount"]
            }
        ),
        (
            "Advanced options",
            {
                "classes": ["collapse"],
                "fields": ["recipe"]
            }
        )
    ]


# Register your models here.
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
