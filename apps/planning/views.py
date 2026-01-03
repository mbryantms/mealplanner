from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.recipes.models import Recipe

from .forms import MealMoveForm, MealPlanForm, QuickMealForm
from .models import MealPlan, MealType


def get_week_dates(target_date):
    """Get the start and end dates of the week containing target_date (Sunday start)."""
    # Find Sunday of the current week
    days_since_sunday = target_date.weekday() + 1
    if days_since_sunday == 7:  # If it's Sunday
        days_since_sunday = 0
    start_of_week = target_date - timedelta(days=days_since_sunday)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


def get_week_data(start_date):
    """Build the week data structure with meals for each day/slot."""
    days = []
    for i in range(7):
        day_date = start_date + timedelta(days=i)
        day_data = {
            "date": day_date,
            "is_today": day_date == date.today(),
            "meals": {
                MealType.BREAKFAST: [],
                MealType.LUNCH: [],
                MealType.DINNER: [],
            },
        }
        days.append(day_data)

    # Fetch all meals for the week
    end_date = start_date + timedelta(days=6)
    meals = MealPlan.objects.filter(
        date__gte=start_date, date__lte=end_date
    ).select_related("recipe")

    # Assign meals to their slots (now as lists)
    for meal in meals:
        day_index = (meal.date - start_date).days
        if 0 <= day_index < 7:
            days[day_index]["meals"][meal.meal_type].append(meal)

    return days


@login_required
def calendar_view(request, date=None):
    """Display the weekly meal planning calendar."""
    # Parse date or default to today
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            target_date = datetime.today().date()
    else:
        target_date = datetime.today().date()

    # Get week boundaries
    start_of_week, end_of_week = get_week_dates(target_date)

    # Get week data
    days = get_week_data(start_of_week)

    # Navigation dates
    prev_week = start_of_week - timedelta(days=7)
    next_week = start_of_week + timedelta(days=7)

    is_htmx = request.headers.get("HX-Request")

    context = {
        "days": days,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "prev_week": prev_week,
        "next_week": next_week,
        "today": datetime.today().date(),
        "meal_types": MealType,
        "is_htmx": is_htmx,
    }

    # Return partial for HTMX requests
    if is_htmx:
        return render(request, "planning/partials/calendar_grid.html", context)

    return render(request, "planning/calendar.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def meal_add(request):
    """Add a new meal to the plan."""
    if request.method == "POST":
        form = QuickMealForm(request.POST)
        if form.is_valid():
            meal_date = form.cleaned_data["date"]
            meal_type = form.cleaned_data["meal_type"]
            recipe = form.cleaned_data.get("recipe")
            custom_meal = form.cleaned_data.get("custom_meal", "")

            # Always create a new meal (multiple meals per slot allowed)
            meal = MealPlan.objects.create(
                date=meal_date,
                meal_type=meal_type,
                recipe=recipe,
                custom_meal=custom_meal if not recipe else "",
            )

            # Return the updated slot with all meals for this slot
            if request.headers.get("HX-Request"):
                meals = list(MealPlan.objects.filter(
                    date=meal_date, meal_type=meal_type
                ).select_related("recipe"))
                return render(
                    request,
                    "planning/partials/meal_slot.html",
                    {"meals": meals, "date": meal_date, "meal_type": meal_type},
                )

            messages.success(request, "Meal added to plan.")
            return redirect("planning:calendar")

        # Return form with errors for HTMX
        if request.headers.get("HX-Request"):
            return render(
                request,
                "planning/partials/meal_add_form.html",
                {"form": form},
            )

    # GET request - show form
    initial = {
        "date": request.GET.get("date", date.today().isoformat()),
        "meal_type": request.GET.get("meal_type", MealType.DINNER),
    }
    form = QuickMealForm(initial=initial)
    recipes = Recipe.objects.all().order_by("name")

    # Get suggested recipes - prioritize variety by deprioritizing recently used
    from django.db.models import Count

    # Get recipes used in the last week (to deprioritize)
    one_week_ago = date.today() - timedelta(days=7)
    recent_recipe_ids = set(
        MealPlan.objects.filter(date__gte=one_week_ago, recipe__isnull=False)
        .values_list("recipe_id", flat=True)
        .distinct()
    )

    # Step 1: Frequently used recipes NOT used in the last week
    suggested_recipes = list(
        Recipe.objects.filter(meal_plans__isnull=False)
        .exclude(pk__in=recent_recipe_ids)
        .annotate(use_count=Count("meal_plans"))
        .order_by("-use_count")[:6]
    )

    # Step 2: If need more, add other recipes not used recently
    if len(suggested_recipes) < 6:
        other_recipes = Recipe.objects.exclude(
            pk__in=[r.pk for r in suggested_recipes]
        ).exclude(pk__in=recent_recipe_ids)[:6 - len(suggested_recipes)]
        suggested_recipes.extend(other_recipes)

    # Step 3: If still need more, add recently used (sorted by frequency)
    if len(suggested_recipes) < 6:
        recent_frequent = (
            Recipe.objects.filter(pk__in=recent_recipe_ids)
            .exclude(pk__in=[r.pk for r in suggested_recipes])
            .annotate(use_count=Count("meal_plans"))
            .order_by("-use_count")[:6 - len(suggested_recipes)]
        )
        suggested_recipes.extend(recent_frequent)

    # Step 4: If STILL need more, fill with any remaining recipes
    if len(suggested_recipes) < 6:
        remaining = Recipe.objects.exclude(
            pk__in=[r.pk for r in suggested_recipes]
        )[:6 - len(suggested_recipes)]
        suggested_recipes.extend(remaining)

    context = {
        "form": form,
        "recipes": recipes,
        "suggested_recipes": suggested_recipes,
        "date": initial["date"],
        "meal_type": initial["meal_type"],
    }

    if request.headers.get("HX-Request"):
        return render(request, "planning/partials/meal_add_form.html", context)

    return render(request, "planning/meal_add.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def meal_edit(request, pk):
    """Edit an existing meal."""
    meal = get_object_or_404(MealPlan, pk=pk)

    if request.method == "POST":
        form = MealPlanForm(request.POST, instance=meal)
        if form.is_valid():
            form.save()

            if request.headers.get("HX-Request"):
                # Return all meals for this slot
                meals = list(MealPlan.objects.filter(
                    date=meal.date, meal_type=meal.meal_type
                ).select_related("recipe"))
                return render(
                    request,
                    "planning/partials/meal_slot.html",
                    {"meals": meals, "date": meal.date, "meal_type": meal.meal_type},
                )

            messages.success(request, "Meal updated.")
            return redirect("planning:calendar")
    else:
        form = MealPlanForm(instance=meal)

    context = {"form": form, "meal": meal}

    if request.headers.get("HX-Request"):
        return render(request, "planning/partials/meal_edit_form.html", context)

    return render(request, "planning/meal_edit.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def meal_delete(request, pk):
    """Delete a meal from the plan."""
    meal = get_object_or_404(MealPlan, pk=pk)

    if request.method == "POST":
        meal_date = meal.date
        meal_type = meal.meal_type
        meal.delete()

        if request.headers.get("HX-Request"):
            # Return remaining meals for this slot
            meals = list(MealPlan.objects.filter(
                date=meal_date, meal_type=meal_type
            ).select_related("recipe"))
            return render(
                request,
                "planning/partials/meal_slot.html",
                {"meals": meals, "date": meal_date, "meal_type": meal_type},
            )

        messages.success(request, "Meal removed from plan.")
        return redirect("planning:calendar")

    context = {"meal": meal}

    if request.headers.get("HX-Request"):
        return render(request, "planning/partials/meal_delete_confirm.html", context)

    return render(request, "planning/meal_delete.html", context)


@login_required
@require_POST
def meal_move(request, pk):
    """Move a meal to a different date/slot (for drag-and-drop)."""
    meal = get_object_or_404(MealPlan, pk=pk)

    new_date_str = request.POST.get("new_date")
    new_meal_type = request.POST.get("new_meal_type")

    if not new_date_str or not new_meal_type:
        return HttpResponse("Missing date or meal type", status=400)

    try:
        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    if new_meal_type not in [mt.value for mt in MealType]:
        return HttpResponse("Invalid meal type", status=400)

    # Store old slot info
    old_date = meal.date
    old_meal_type = meal.meal_type

    # Check if target slot is occupied
    existing = MealPlan.objects.filter(date=new_date, meal_type=new_meal_type).first()
    if existing and existing.pk != meal.pk:
        # Swap the meals
        existing.date = old_date
        existing.meal_type = old_meal_type
        existing.save()

    # Move the meal
    meal.date = new_date
    meal.meal_type = new_meal_type
    meal.save()

    # Return success - the frontend will handle refreshing the calendar
    return HttpResponse(status=200)


@login_required
@require_POST
def meal_copy(request, pk):
    """Copy a meal to a different date/slot."""
    meal = get_object_or_404(MealPlan, pk=pk)

    new_date_str = request.POST.get("new_date")
    new_meal_type = request.POST.get("new_meal_type")

    if not new_date_str or not new_meal_type:
        return HttpResponse("Missing date or meal type", status=400)

    try:
        new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

    # Always create a new meal (multiple meals per slot allowed)
    MealPlan.objects.create(
        date=new_date,
        meal_type=new_meal_type,
        recipe=meal.recipe,
        custom_meal=meal.custom_meal,
        servings_override=meal.servings_override,
    )

    # Return the updated slot with all meals
    if request.headers.get("HX-Request"):
        meals = list(MealPlan.objects.filter(
            date=new_date, meal_type=new_meal_type
        ).select_related("recipe"))
        return render(
            request,
            "planning/partials/meal_slot.html",
            {
                "meals": meals,
                "date": new_date,
                "meal_type": new_meal_type,
            },
        )

    return HttpResponse(status=200)


@login_required
@require_GET
def recipe_search(request):
    """Search recipes for meal assignment."""
    query = request.GET.get("q", "").strip()

    recipes = Recipe.objects.all()
    if query:
        recipes = recipes.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    recipes = recipes.order_by("name")[:10]

    return render(
        request,
        "planning/partials/recipe_search_results.html",
        {"recipes": recipes, "query": query},
    )


@login_required
@require_GET
def day_slot(request, date, meal_type):
    """Get a single day slot (for HTMX refresh after drag-drop)."""
    try:
        slot_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date", status=400)

    meals = list(MealPlan.objects.filter(
        date=slot_date, meal_type=meal_type
    ).select_related("recipe"))

    return render(
        request,
        "planning/partials/meal_slot.html",
        {"meals": meals, "date": slot_date, "meal_type": meal_type},
    )
