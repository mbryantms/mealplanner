from django.contrib import admin

from .models import ShoppingList, ShoppingListItem


class ShoppingListItemInline(admin.TabularInline):
    model = ShoppingListItem
    extra = 1
    autocomplete_fields = ["ingredient", "category_override"]
    fields = [
        "ingredient",
        "custom_item",
        "quantity",
        "unit",
        "checked",
        "category_override",
    ]


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ["name", "date_range", "progress", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at"]
    inlines = [ShoppingListItemInline]
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Date Range", {"fields": ["start_date", "end_date"]}),
        ("Metadata", {"fields": ["created_at"], "classes": ["collapse"]}),
    ]

    def progress(self, obj):
        return f"{obj.checked_count}/{obj.total_count} ({obj.progress_percent}%)"

    progress.short_description = "Progress"


@admin.register(ShoppingListItem)
class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = [
        "display_name",
        "shopping_list",
        "quantity",
        "unit",
        "category",
        "checked",
    ]
    list_filter = ["shopping_list", "checked", "ingredient__category"]
    search_fields = ["ingredient__name", "custom_item"]
    autocomplete_fields = ["shopping_list", "ingredient", "category_override"]
    list_editable = ["checked"]
