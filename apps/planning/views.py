from datetime import date, datetime, timedelta

from django.contrib import messages
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
                MealType.BREAKFAST: None,
                MealType.LUNCH: None,
                MealType.DINNER: None,
            },
        }
        days.append(day_data)

    # Fetch all meals for the week
    end_date = start_date + timedelta(days=6)
    meals = MealPlan.objects.filter(
        date__gte=start_date, date__lte=end_date
    ).select_related("recipe")

    # Assign meals to their slots
    for meal in meals:
        day_index = (meal.date - start_date).days
        if 0 <= day_index < 7:
            days[day_index]["meals"][meal.meal_type] = meal

    return days


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

    context = {
        "days": days,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "prev_week": prev_week,
        "next_week": next_week,
        "today": datetime.today().date(),
        "meal_types": MealType,
    }

    # Return partial for HTMX requests
    if request.headers.get("HX-Request"):
        return render(request, "planning/partials/calendar_grid.html", context)

    return render(request, "planning/calendar.html", context)


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

            # Check if slot is already occupied
            existing = MealPlan.objects.filter(date=meal_date, meal_type=meal_type).first()
            if existing:
                existing.recipe = recipe
                existing.custom_meal = custom_meal if not recipe else ""
                existing.save()
                meal = existing
            else:
                meal = MealPlan.objects.create(
                    date=meal_date,
                    meal_type=meal_type,
                    recipe=recipe,
                    custom_meal=custom_meal if not recipe else "",
                )

            # Return the updated slot
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "planning/partials/meal_slot.html",
                    {"meal": meal, "date": meal_date, "meal_type": meal_type},
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

    context = {
        "form": form,
        "recipes": recipes,
        "date": initial["date"],
        "meal_type": initial["meal_type"],
    }

    if request.headers.get("HX-Request"):
        return render(request, "planning/partials/meal_add_form.html", context)

    return render(request, "planning/meal_add.html", context)


@require_http_methods(["GET", "POST"])
def meal_edit(request, pk):
    """Edit an existing meal."""
    meal = get_object_or_404(MealPlan, pk=pk)

    if request.method == "POST":
        form = MealPlanForm(request.POST, instance=meal)
        if form.is_valid():
            form.save()

            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "planning/partials/meal_slot.html",
                    {"meal": meal, "date": meal.date, "meal_type": meal.meal_type},
                )

            messages.success(request, "Meal updated.")
            return redirect("planning:calendar")
    else:
        form = MealPlanForm(instance=meal)

    context = {"form": form, "meal": meal}

    if request.headers.get("HX-Request"):
        return render(request, "planning/partials/meal_edit_form.html", context)

    return render(request, "planning/meal_edit.html", context)


@require_http_methods(["GET", "POST"])
def meal_delete(request, pk):
    """Delete a meal from the plan."""
    meal = get_object_or_404(MealPlan, pk=pk)

    if request.method == "POST":
        meal_date = meal.date
        meal_type = meal.meal_type
        meal.delete()

        if request.headers.get("HX-Request"):
            # Return empty slot
            return render(
                request,
                "planning/partials/meal_slot.html",
                {"meal": None, "date": meal_date, "meal_type": meal_type},
            )

        messages.success(request, "Meal removed from plan.")
        return redirect("planning:calendar")

    context = {"meal": meal}

    if request.headers.get("HX-Request"):
        return render(request, "planning/partials/meal_delete_confirm.html", context)

    return render(request, "planning/meal_delete.html", context)


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

    # Check if target slot is occupied
    existing = MealPlan.objects.filter(date=new_date, meal_type=new_meal_type).first()
    if existing:
        # Update existing
        existing.recipe = meal.recipe
        existing.custom_meal = meal.custom_meal
        existing.servings_override = meal.servings_override
        existing.save()
    else:
        # Create new
        MealPlan.objects.create(
            date=new_date,
            meal_type=new_meal_type,
            recipe=meal.recipe,
            custom_meal=meal.custom_meal,
            servings_override=meal.servings_override,
        )

    # Return the updated slot
    if request.headers.get("HX-Request"):
        return render(
            request,
            "planning/partials/meal_slot.html",
            {
                "meal": MealPlan.objects.get(date=new_date, meal_type=new_meal_type),
                "date": new_date,
                "meal_type": new_meal_type,
            },
        )

    return HttpResponse(status=200)


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


@require_GET
def day_slot(request, date, meal_type):
    """Get a single day slot (for HTMX refresh after drag-drop)."""
    try:
        slot_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponse("Invalid date", status=400)

    meal = MealPlan.objects.filter(date=slot_date, meal_type=meal_type).first()

    return render(
        request,
        "planning/partials/meal_slot.html",
        {"meal": meal, "date": slot_date, "meal_type": meal_type},
    )
