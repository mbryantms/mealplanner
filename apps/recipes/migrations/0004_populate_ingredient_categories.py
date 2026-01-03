# Generated manually for data population

from django.db import migrations


def populate_ingredient_categories(apps, schema_editor):
    """Populate default ingredient categories for grocery store organization."""
    IngredientCategory = apps.get_model("recipes", "IngredientCategory")

    categories = [
        {"name": "Produce", "sort_order": 10},
        {"name": "Meat & Seafood", "sort_order": 20},
        {"name": "Dairy & Eggs", "sort_order": 30},
        {"name": "Deli & Prepared Foods", "sort_order": 40},
        {"name": "Bakery & Bread", "sort_order": 50},
        {"name": "Frozen", "sort_order": 60},
        {"name": "Canned Goods", "sort_order": 70},
        {"name": "Pasta & Grains", "sort_order": 80},
        {"name": "Sauces & Condiments", "sort_order": 90},
        {"name": "Oils & Vinegars", "sort_order": 100},
        {"name": "Spices & Seasonings", "sort_order": 110},
        {"name": "Baking", "sort_order": 120},
        {"name": "Snacks", "sort_order": 130},
        {"name": "Beverages", "sort_order": 140},
        {"name": "International", "sort_order": 150},
        {"name": "Health & Organic", "sort_order": 160},
        {"name": "Household", "sort_order": 170},
    ]

    for cat_data in categories:
        IngredientCategory.objects.get_or_create(
            name=cat_data["name"],
            defaults={"sort_order": cat_data["sort_order"]},
        )


def reverse_populate(apps, schema_editor):
    """Remove the default categories (only if empty)."""
    IngredientCategory = apps.get_model("recipes", "IngredientCategory")
    default_names = [
        "Produce",
        "Meat & Seafood",
        "Dairy & Eggs",
        "Deli & Prepared Foods",
        "Bakery & Bread",
        "Frozen",
        "Canned Goods",
        "Pasta & Grains",
        "Sauces & Condiments",
        "Oils & Vinegars",
        "Spices & Seasonings",
        "Baking",
        "Snacks",
        "Beverages",
        "International",
        "Health & Organic",
        "Household",
    ]
    # Only delete if no ingredients are using them
    for name in default_names:
        try:
            cat = IngredientCategory.objects.get(name=name)
            if cat.ingredients.count() == 0:
                cat.delete()
        except IngredientCategory.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0003_replace_category_with_cuisine_protein_dishtype"),
    ]

    operations = [
        migrations.RunPython(populate_ingredient_categories, reverse_populate),
    ]
