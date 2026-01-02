from django.urls import path

from . import views

app_name = "recipes"

urlpatterns = [
    # Recipe CRUD
    path("", views.recipe_list, name="recipe_list"),
    path("create/", views.recipe_create, name="recipe_create"),
    path("<int:pk>/", views.recipe_detail, name="recipe_detail"),
    path("<int:pk>/edit/", views.recipe_edit, name="recipe_edit"),
    path("<int:pk>/delete/", views.recipe_delete, name="recipe_delete"),
    # HTMX endpoints
    path(
        "ingredients/autocomplete/",
        views.ingredient_autocomplete,
        name="ingredient_autocomplete",
    ),
    path(
        "ingredients/create-inline/",
        views.ingredient_create_inline,
        name="ingredient_create_inline",
    ),
    path(
        "categories/create-inline/",
        views.category_create_inline,
        name="category_create_inline",
    ),
    path("tags/create-inline/", views.tag_create_inline, name="tag_create_inline"),
    # Recipe ingredient management (HTMX)
    path(
        "<int:pk>/ingredients/add/",
        views.recipe_ingredient_add,
        name="recipe_ingredient_add",
    ),
    path(
        "recipe-ingredients/<int:pk>/remove/",
        views.recipe_ingredient_remove,
        name="recipe_ingredient_remove",
    ),
    path(
        "recipe-ingredients/<int:pk>/update/",
        views.recipe_ingredient_update,
        name="recipe_ingredient_update",
    ),
]
