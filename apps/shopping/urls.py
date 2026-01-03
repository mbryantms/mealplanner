from django.urls import path

from . import views

app_name = "shopping"

urlpatterns = [
    # Shopping list views
    path("", views.shopping_list_list, name="list"),
    path("create/", views.shopping_list_create, name="create"),
    path("generate/", views.shopping_list_generate, name="generate"),
    path("<int:pk>/", views.shopping_list_detail, name="detail"),
    path("<int:pk>/edit/", views.shopping_list_edit, name="edit"),
    path("<int:pk>/delete/", views.shopping_list_delete, name="delete"),
    # Item management
    path("<int:pk>/items/add/", views.item_add, name="item_add"),
    path("items/<int:pk>/toggle/", views.item_toggle, name="item_toggle"),
    path("items/<int:pk>/update/", views.item_update, name="item_update"),
    path("items/<int:pk>/delete/", views.item_delete, name="item_delete"),
    # Bulk actions
    path("<int:pk>/clear-checked/", views.clear_checked, name="clear_checked"),
    path("<int:pk>/uncheck-all/", views.uncheck_all, name="uncheck_all"),
]
