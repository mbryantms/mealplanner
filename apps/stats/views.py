"""Views for statistics dashboard."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from . import services


@login_required
def dashboard(request):
    """Main dashboard view with all statistics."""
    # Get date range from query params (default: last 30 days)
    days = int(request.GET.get("days", 30))

    # Get max counts for percentage calculations in charts
    top_recipes = list(services.get_recipe_usage_stats(limit=10))
    max_recipe_usage = top_recipes[0].usage_count if top_recipes else 1

    top_ingredients = list(services.get_most_used_ingredients(limit=10))
    max_ingredient_usage = top_ingredients[0].meal_count if top_ingredients else 1

    day_of_week_stats = services.get_day_of_week_stats()
    max_day_count = max((d["count"] for d in day_of_week_stats), default=1)

    context = {
        "overview": services.get_overview_stats(),
        "top_recipes": top_recipes,
        "max_recipe_usage": max_recipe_usage,
        "never_used_recipes": services.get_never_used_recipes(limit=5),
        "day_of_week_stats": day_of_week_stats,
        "max_day_count": max_day_count,
        "weekend_vs_weekday": services.get_weekend_vs_weekday_stats(),
        "popular_weekend_recipes": services.get_popular_weekend_recipes(limit=5),
        "top_ingredients": top_ingredients,
        "max_ingredient_usage": max_ingredient_usage,
        "ingredient_categories": services.get_ingredient_category_breakdown(),
        "cuisine_breakdown": services.get_cuisine_breakdown(),
        "protein_breakdown": services.get_protein_breakdown(),
        "dish_type_breakdown": services.get_dish_type_breakdown(),
        "meal_type_breakdown": services.get_meal_type_breakdown(),
        "planning_coverage": services.get_planning_coverage(days=days),
        "weekly_trends": services.get_weekly_trends(weeks=12),
        "monthly_trends": services.get_monthly_trends(months=6),
        "days_filter": days,
        "days_options": [7, 14, 30, 60, 90],
    }

    return render(request, "stats/dashboard.html", context)
