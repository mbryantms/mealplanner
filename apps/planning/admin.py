from django.contrib import admin

from .models import MealPlan


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ["date", "meal_type", "meal_name", "servings", "has_notes"]
    list_filter = ["meal_type", "date"]
    search_fields = ["recipe__name", "custom_meal", "notes"]
    autocomplete_fields = ["recipe"]
    date_hierarchy = "date"
    ordering = ["-date", "meal_type"]
    fieldsets = [
        (None, {"fields": ["date", "meal_type"]}),
        ("Meal", {"fields": ["recipe", "custom_meal"]}),
        ("Options", {"fields": ["servings_override", "notes"]}),
    ]

    def meal_name(self, obj):
        if obj.recipe:
            return obj.recipe.name
        return obj.custom_meal or "—"

    meal_name.short_description = "Meal"

    def has_notes(self, obj):
        return bool(obj.notes)

    has_notes.boolean = True
    has_notes.short_description = "Notes"
