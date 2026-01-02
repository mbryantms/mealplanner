from django.urls import path

from . import views

app_name = "planning"

urlpatterns = [
    # Calendar views
    path("", views.calendar_view, name="calendar"),
    path("week/<str:date>/", views.calendar_view, name="calendar_week"),
    # Meal CRUD
    path("meal/add/", views.meal_add, name="meal_add"),
    path("meal/<int:pk>/edit/", views.meal_edit, name="meal_edit"),
    path("meal/<int:pk>/delete/", views.meal_delete, name="meal_delete"),
    path("meal/<int:pk>/move/", views.meal_move, name="meal_move"),
    path("meal/<int:pk>/copy/", views.meal_copy, name="meal_copy"),
    # HTMX endpoints
    path("recipe-search/", views.recipe_search, name="recipe_search"),
    path("day/<str:date>/<str:meal_type>/", views.day_slot, name="day_slot"),
]
