"""Statistics aggregation services."""

from datetime import date, timedelta

from django.db.models import Count, Q
from django.db.models.functions import ExtractWeekDay, TruncMonth, TruncWeek

from apps.planning.models import MealPlan
from apps.recipes.models import (
    Cuisine,
    DishType,
    Ingredient,
    IngredientCategory,
    Protein,
    Recipe,
)
from apps.shopping.models import ShoppingList


def get_overview_stats():
    """Get basic counts for the overview cards."""
    today = date.today()
    # Find start of current week (Sunday)
    days_since_sunday = (today.weekday() + 1) % 7
    start_of_week = today - timedelta(days=days_since_sunday)
    end_of_week = start_of_week + timedelta(days=6)

    return {
        "total_recipes": Recipe.objects.count(),
        "total_ingredients": Ingredient.objects.count(),
        "total_meals_planned": MealPlan.objects.count(),
        "meals_this_week": MealPlan.objects.filter(
            date__gte=start_of_week, date__lte=end_of_week
        ).count(),
        "shopping_lists": ShoppingList.objects.count(),
    }


def get_recipe_usage_stats(limit=10):
    """Get most used recipes with usage counts."""
    return (
        Recipe.objects.annotate(usage_count=Count("meal_plans"))
        .filter(usage_count__gt=0)
        .order_by("-usage_count")[:limit]
    )


def get_never_used_recipes(limit=10):
    """Get recipes that have never been planned."""
    return (
        Recipe.objects.annotate(usage_count=Count("meal_plans"))
        .filter(usage_count=0)
        .order_by("name")[:limit]
    )


def get_day_of_week_stats():
    """
    Get meal counts by day of week.

    Django's ExtractWeekDay: 1=Sunday, 2=Monday, ... 7=Saturday
    """
    stats = (
        MealPlan.objects.filter(recipe__isnull=False)
        .annotate(day_of_week=ExtractWeekDay("date"))
        .values("day_of_week")
        .annotate(count=Count("id"))
        .order_by("day_of_week")
    )

    # Convert to list with all days, filling in zeros for missing days
    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    stats_dict = {s["day_of_week"]: s["count"] for s in stats}

    return [
        {"day": day_names[i], "day_of_week": i + 1, "count": stats_dict.get(i + 1, 0)}
        for i in range(7)
    ]


def get_weekend_vs_weekday_stats():
    """Compare weekend vs weekday meal planning."""
    # Weekend = Saturday (7) and Sunday (1)
    weekend_meals = (
        MealPlan.objects.filter(recipe__isnull=False)
        .annotate(day_of_week=ExtractWeekDay("date"))
        .filter(Q(day_of_week=1) | Q(day_of_week=7))
        .count()
    )

    weekday_meals = (
        MealPlan.objects.filter(recipe__isnull=False)
        .annotate(day_of_week=ExtractWeekDay("date"))
        .exclude(Q(day_of_week=1) | Q(day_of_week=7))
        .count()
    )

    return {
        "weekend": weekend_meals,
        "weekday": weekday_meals,
    }


def get_popular_weekend_recipes(limit=5):
    """Get most popular recipes for weekends (Saturday/Sunday)."""
    return (
        Recipe.objects.annotate(
            weekend_count=Count(
                "meal_plans",
                filter=Q(meal_plans__date__week_day__in=[1, 7]),
            )
        )
        .filter(weekend_count__gt=0)
        .order_by("-weekend_count")[:limit]
    )


def get_most_used_ingredients(limit=10):
    """Get most used ingredients across all planned meals."""
    return (
        Ingredient.objects.annotate(
            recipe_count=Count("recipes", distinct=True),
            meal_count=Count("recipes__meal_plans"),
        )
        .filter(meal_count__gt=0)
        .order_by("-meal_count")[:limit]
    )


def get_ingredient_category_breakdown():
    """Get ingredient counts by category."""
    return (
        IngredientCategory.objects.annotate(
            ingredient_count=Count("ingredients"),
            usage_in_recipes=Count("ingredients__recipes", distinct=True),
        )
        .filter(ingredient_count__gt=0)
        .order_by("-usage_in_recipes")
    )


def get_cuisine_breakdown():
    """Get meal plan counts by cuisine."""
    return (
        Cuisine.objects.annotate(
            recipe_count=Count("recipes"),
            meal_count=Count("recipes__meal_plans"),
        )
        .filter(recipe_count__gt=0)
        .order_by("-meal_count")
    )


def get_protein_breakdown():
    """Get meal plan counts by protein type."""
    return (
        Protein.objects.annotate(
            recipe_count=Count("recipes"),
            meal_count=Count("recipes__meal_plans"),
        )
        .filter(recipe_count__gt=0)
        .order_by("-meal_count")
    )


def get_dish_type_breakdown():
    """Get meal plan counts by dish type."""
    return (
        DishType.objects.annotate(
            recipe_count=Count("recipes"),
            meal_count=Count("recipes__meal_plans"),
        )
        .filter(recipe_count__gt=0)
        .order_by("-meal_count")
    )


def get_planning_coverage(days=30):
    """Calculate meal planning coverage for the past N days."""
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    # Total possible meal slots (3 meals per day)
    total_days = days
    total_slots = total_days * 3

    # Actual planned meals
    planned_meals = MealPlan.objects.filter(
        date__gte=start_date, date__lte=end_date
    ).count()

    # Days with at least one meal planned
    days_with_meals = (
        MealPlan.objects.filter(date__gte=start_date, date__lte=end_date)
        .values("date")
        .distinct()
        .count()
    )

    return {
        "total_days": total_days,
        "days_with_meals": days_with_meals,
        "coverage_percent": (
            round((days_with_meals / total_days) * 100, 1) if total_days > 0 else 0
        ),
        "planned_meals": planned_meals,
        "total_slots": total_slots,
        "slot_coverage_percent": (
            round((planned_meals / total_slots) * 100, 1) if total_slots > 0 else 0
        ),
        "start_date": start_date,
        "end_date": end_date,
    }


def get_weekly_trends(weeks=12):
    """Get meal counts per week for the past N weeks."""
    start_date = date.today() - timedelta(weeks=weeks)

    return list(
        MealPlan.objects.filter(date__gte=start_date)
        .annotate(week=TruncWeek("date"))
        .values("week")
        .annotate(
            count=Count("id"),
            recipe_count=Count("id", filter=Q(recipe__isnull=False)),
            custom_count=Count("id", filter=Q(recipe__isnull=True)),
        )
        .order_by("week")
    )


def get_monthly_trends(months=6):
    """Get meal counts per month for the past N months."""
    start_date = date.today() - timedelta(days=months * 30)

    return list(
        MealPlan.objects.filter(date__gte=start_date)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(
            count=Count("id"),
            recipe_count=Count("id", filter=Q(recipe__isnull=False)),
            unique_recipes=Count("recipe", distinct=True),
        )
        .order_by("month")
    )


def get_meal_type_breakdown():
    """Get counts by meal type (breakfast, lunch, dinner)."""
    stats = (
        MealPlan.objects.values("meal_type")
        .annotate(count=Count("id"))
        .order_by("meal_type")
    )

    # Map to friendly names
    meal_type_names = {
        "breakfast": "Breakfast",
        "lunch": "Lunch",
        "dinner": "Dinner",
    }

    return [
        {
            "meal_type": s["meal_type"],
            "name": meal_type_names.get(s["meal_type"], s["meal_type"].title()),
            "count": s["count"],
        }
        for s in stats
    ]
