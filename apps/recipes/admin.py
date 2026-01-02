from django.contrib import admin

from .models import (
    Category,
    Ingredient,
    IngredientCategory,
    Recipe,
    RecipeIngredient,
    Tag,
)


@admin.register(IngredientCategory)
class IngredientCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "sort_order", "ingredient_count"]
    list_editable = ["sort_order"]
    search_fields = ["name"]
    ordering = ["sort_order", "name"]

    def ingredient_count(self, obj):
        return obj.ingredients.count()

    ingredient_count.short_description = "Ingredients"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "default_unit"]
    list_filter = ["category"]
    search_fields = ["name", "notes"]
    autocomplete_fields = ["category"]
    ordering = ["name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "recipe_count"]
    list_filter = ["parent"]
    search_fields = ["name"]
    autocomplete_fields = ["parent"]

    def recipe_count(self, obj):
        return obj.recipes.count()

    recipe_count.short_description = "Recipes"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "recipe_count"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

    def recipe_count(self, obj):
        return obj.recipes.count()

    recipe_count.short_description = "Recipes"


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ["ingredient"]
    fields = ["ingredient", "quantity", "unit", "preparation", "optional", "order"]
    ordering = ["order"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "servings",
        "total_time",
        "makes_leftovers",
        "created_at",
    ]
    list_filter = ["category", "tags", "makes_leftovers"]
    search_fields = ["name", "description", "instructions"]
    autocomplete_fields = ["category"]
    filter_horizontal = ["tags"]
    inlines = [RecipeIngredientInline]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        (None, {"fields": ["name", "description", "image"]}),
        (
            "Times & Servings",
            {"fields": ["prep_time", "cook_time", "servings"]},
        ),
        (
            "Leftovers",
            {
                "fields": ["makes_leftovers", "leftover_days"],
                "classes": ["collapse"],
            },
        ),
        ("Instructions", {"fields": ["instructions"]}),
        ("Organization", {"fields": ["category", "tags"]}),
        (
            "Source",
            {
                "fields": ["source_url"],
                "classes": ["collapse"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at"],
                "classes": ["collapse"],
            },
        ),
    ]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ["recipe", "ingredient", "quantity", "unit", "optional"]
    list_filter = ["recipe", "optional"]
    search_fields = ["recipe__name", "ingredient__name"]
    autocomplete_fields = ["recipe", "ingredient"]
