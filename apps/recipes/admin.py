from django.contrib import admin

from .models import (
    Cuisine,
    DishType,
    Ingredient,
    IngredientCategory,
    Protein,
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


@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ["name", "recipe_count"]
    search_fields = ["name"]

    def recipe_count(self, obj):
        return obj.recipes.count()

    recipe_count.short_description = "Recipes"


@admin.register(Protein)
class ProteinAdmin(admin.ModelAdmin):
    list_display = ["name", "recipe_count"]
    search_fields = ["name"]

    def recipe_count(self, obj):
        return obj.recipes.count()

    recipe_count.short_description = "Recipes"


@admin.register(DishType)
class DishTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "recipe_count"]
    search_fields = ["name"]

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
        "get_cuisines",
        "get_proteins",
        "get_dish_types",
        "servings",
        "total_time",
        "makes_leftovers",
        "created_at",
    ]
    list_filter = ["cuisines", "proteins", "dish_types", "tags", "makes_leftovers"]
    search_fields = ["name", "description", "instructions"]
    filter_horizontal = ["cuisines", "proteins", "dish_types", "tags"]
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
        ("Classification", {"fields": ["cuisines", "proteins", "dish_types", "tags"]}),
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

    def get_cuisines(self, obj):
        return ", ".join([c.name for c in obj.cuisines.all()])

    get_cuisines.short_description = "Cuisines"

    def get_proteins(self, obj):
        return ", ".join([p.name for p in obj.proteins.all()])

    get_proteins.short_description = "Proteins"

    def get_dish_types(self, obj):
        return ", ".join([d.name for d in obj.dish_types.all()])

    get_dish_types.short_description = "Dish Types"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ["recipe", "ingredient", "quantity", "unit", "optional"]
    list_filter = ["recipe", "optional"]
    search_fields = ["recipe__name", "ingredient__name"]
    autocomplete_fields = ["recipe", "ingredient"]
