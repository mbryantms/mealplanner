from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from apps.planning.models import MealPlan
from apps.recipes.models import Ingredient

from .forms import GenerateFromMealPlanForm, QuickItemForm, ShoppingListForm
from .models import ShoppingList, ShoppingListItem


@login_required
def shopping_list_list(request):
    """Display all shopping lists."""
    lists = ShoppingList.objects.all()
    return render(request, "shopping/shopping_list_list.html", {"lists": lists})


@login_required
@require_http_methods(["GET", "POST"])
def shopping_list_create(request):
    """Create a new empty shopping list."""
    if request.method == "POST":
        form = ShoppingListForm(request.POST)
        if form.is_valid():
            shopping_list = form.save()
            messages.success(request, f"Shopping list '{shopping_list.name}' created.")
            return redirect("shopping:detail", pk=shopping_list.pk)
    else:
        # Default name based on current date
        today = date.today()
        default_name = f"Week of {today.strftime('%b %d')}"
        form = ShoppingListForm(initial={"name": default_name})

    return render(
        request,
        "shopping/shopping_list_form.html",
        {"form": form, "title": "Create Shopping List"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def shopping_list_generate(request):
    """Generate a shopping list from meal plan date range."""
    if request.method == "POST":
        form = GenerateFromMealPlanForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            # Create the shopping list
            shopping_list = ShoppingList.objects.create(
                name=name,
                start_date=start_date,
                end_date=end_date,
            )

            # Get meal plans in date range
            meal_plans = MealPlan.objects.filter(
                date__gte=start_date,
                date__lte=end_date,
                recipe__isnull=False,
            ).select_related("recipe")

            # Aggregate ingredients from all recipes
            ingredient_totals = defaultdict(lambda: {"quantity": Decimal("0"), "unit": ""})

            for meal_plan in meal_plans:
                recipe = meal_plan.recipe
                # Get serving multiplier
                servings = meal_plan.servings or recipe.servings
                multiplier = Decimal(servings) / Decimal(recipe.servings) if recipe.servings else Decimal("1")

                for ri in recipe.recipe_ingredients.select_related("ingredient"):
                    ingredient = ri.ingredient
                    key = ingredient.pk

                    # Calculate scaled quantity
                    if ri.quantity:
                        scaled_qty = ri.quantity * multiplier
                        ingredient_totals[key]["quantity"] += scaled_qty

                    # Use the unit (prefer recipe ingredient unit, fallback to default)
                    unit = ri.unit or ingredient.default_unit or ""
                    if not ingredient_totals[key]["unit"]:
                        ingredient_totals[key]["unit"] = unit

                    # Store ingredient reference
                    ingredient_totals[key]["ingredient"] = ingredient

            # Create shopping list items
            for key, data in ingredient_totals.items():
                ShoppingListItem.objects.create(
                    shopping_list=shopping_list,
                    ingredient=data["ingredient"],
                    quantity=data["quantity"] if data["quantity"] > 0 else None,
                    unit=data["unit"],
                )

            messages.success(
                request,
                f"Shopping list '{name}' generated with {len(ingredient_totals)} items from {meal_plans.count()} meals.",
            )
            return redirect("shopping:detail", pk=shopping_list.pk)
    else:
        # Default to current week
        today = date.today()
        # Find Sunday of current week
        days_since_sunday = (today.weekday() + 1) % 7
        start_of_week = today - timedelta(days=days_since_sunday)
        end_of_week = start_of_week + timedelta(days=6)

        form = GenerateFromMealPlanForm(
            initial={
                "name": f"Week of {start_of_week.strftime('%b %d')}",
                "start_date": start_of_week,
                "end_date": end_of_week,
            }
        )

    return render(
        request,
        "shopping/shopping_list_generate.html",
        {"form": form, "title": "Generate from Meal Plan"},
    )


@login_required
def shopping_list_detail(request, pk):
    """View a shopping list with items optionally grouped by category."""
    shopping_list = get_object_or_404(ShoppingList, pk=pk)
    items = shopping_list.items.select_related(
        "ingredient", "ingredient__category", "category_override"
    )

    # Get sort preference from query param (default to category grouping)
    sort_by = request.GET.get("sort", "category")

    # Quick add form
    quick_form = QuickItemForm()

    context = {
        "shopping_list": shopping_list,
        "quick_form": quick_form,
        "sort_by": sort_by,
    }

    if sort_by == "alphabetical":
        # Sort all items alphabetically
        all_items = sorted(items, key=lambda i: i.display_name.lower())
        context["all_items"] = all_items
        context["categorized_items"] = []
        context["uncategorized"] = []
    else:
        # Group items by category (default)
        grouped_items = defaultdict(list)
        uncategorized = []

        for item in items:
            category = item.category
            if category:
                grouped_items[category].append(item)
            else:
                uncategorized.append(item)

        # Sort categories by sort_order
        sorted_categories = sorted(grouped_items.keys(), key=lambda c: (c.sort_order, c.name))

        # Build ordered list of (category, items) tuples
        categorized_items = [(cat, grouped_items[cat]) for cat in sorted_categories]

        context["categorized_items"] = categorized_items
        context["uncategorized"] = uncategorized
        context["all_items"] = []

    return render(request, "shopping/shopping_list_detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def shopping_list_edit(request, pk):
    """Edit shopping list metadata."""
    shopping_list = get_object_or_404(ShoppingList, pk=pk)

    if request.method == "POST":
        form = ShoppingListForm(request.POST, instance=shopping_list)
        if form.is_valid():
            form.save()
            messages.success(request, "Shopping list updated.")
            return redirect("shopping:detail", pk=pk)
    else:
        form = ShoppingListForm(instance=shopping_list)

    return render(
        request,
        "shopping/shopping_list_form.html",
        {"form": form, "shopping_list": shopping_list, "title": "Edit Shopping List"},
    )


@login_required
@require_http_methods(["GET", "POST"])
def shopping_list_delete(request, pk):
    """Delete a shopping list."""
    shopping_list = get_object_or_404(ShoppingList, pk=pk)

    if request.method == "POST":
        name = shopping_list.name
        shopping_list.delete()
        messages.success(request, f"Shopping list '{name}' deleted.")
        return redirect("shopping:list")

    return render(
        request,
        "shopping/shopping_list_delete.html",
        {"shopping_list": shopping_list},
    )


@login_required
@require_POST
def item_add(request, pk):
    """Add an item to a shopping list via HTMX."""
    shopping_list = get_object_or_404(ShoppingList, pk=pk)
    form = QuickItemForm(request.POST)

    if form.is_valid():
        item_name = form.cleaned_data["item_name"]
        quantity = form.cleaned_data.get("quantity")
        unit = form.cleaned_data.get("unit", "")

        # Try to find matching ingredient
        ingredient = Ingredient.objects.filter(name__iexact=item_name).first()

        if ingredient:
            # Check if item already exists
            existing = shopping_list.items.filter(ingredient=ingredient).first()
            if existing:
                # Update quantity
                if quantity and existing.quantity:
                    existing.quantity += quantity
                elif quantity:
                    existing.quantity = quantity
                existing.save()
                item = existing
            else:
                item = ShoppingListItem.objects.create(
                    shopping_list=shopping_list,
                    ingredient=ingredient,
                    quantity=quantity,
                    unit=unit or ingredient.default_unit or "",
                )
        else:
            # Create as custom item
            item = ShoppingListItem.objects.create(
                shopping_list=shopping_list,
                custom_item=item_name,
                quantity=quantity,
                unit=unit,
            )

        if request.headers.get("HX-Request"):
            item_html = render(
                request,
                "shopping/partials/item_row.html",
                {"item": item, "shopping_list": shopping_list},
            ).content.decode()

            progress_html = render(
                request,
                "shopping/partials/progress_bar.html",
                {"shopping_list": shopping_list},
            ).content.decode()

            return HttpResponse(item_html + progress_html)

    return redirect("shopping:detail", pk=pk)


@login_required
@require_POST
def item_toggle(request, pk):
    """Toggle checked status of an item via HTMX."""
    item = get_object_or_404(ShoppingListItem, pk=pk)
    item.checked = not item.checked
    item.save()

    if request.headers.get("HX-Request"):
        # Render both the item row and progress bar (OOB swap)
        item_html = render(
            request,
            "shopping/partials/item_row.html",
            {"item": item, "shopping_list": item.shopping_list},
        ).content.decode()

        progress_html = render(
            request,
            "shopping/partials/progress_bar.html",
            {"shopping_list": item.shopping_list},
        ).content.decode()

        return HttpResponse(item_html + progress_html)

    return redirect("shopping:detail", pk=item.shopping_list.pk)


@login_required
@require_POST
def item_update(request, pk):
    """Update an item's quantity/unit via HTMX."""
    item = get_object_or_404(ShoppingListItem, pk=pk)

    quantity = request.POST.get("quantity")
    unit = request.POST.get("unit")

    if quantity:
        try:
            item.quantity = Decimal(quantity)
        except (ValueError, TypeError):
            pass

    if unit is not None:
        item.unit = unit

    item.save()

    if request.headers.get("HX-Request"):
        return render(
            request,
            "shopping/partials/item_row.html",
            {"item": item, "shopping_list": item.shopping_list},
        )

    return redirect("shopping:detail", pk=item.shopping_list.pk)


@login_required
@require_POST
def item_delete(request, pk):
    """Delete an item via HTMX."""
    item = get_object_or_404(ShoppingListItem, pk=pk)
    shopping_list = item.shopping_list
    item.delete()

    if request.headers.get("HX-Request"):
        # Return empty string to remove item, plus OOB progress bar update
        progress_html = render(
            request,
            "shopping/partials/progress_bar.html",
            {"shopping_list": shopping_list},
        ).content.decode()
        return HttpResponse(progress_html)

    return redirect("shopping:detail", pk=shopping_list.pk)


@login_required
@require_POST
def clear_checked(request, pk):
    """Remove all checked items from a shopping list."""
    shopping_list = get_object_or_404(ShoppingList, pk=pk)
    count = shopping_list.items.filter(checked=True).delete()[0]

    if request.headers.get("HX-Request"):
        # Re-fetch and group items for the response
        items = shopping_list.items.select_related(
            "ingredient", "ingredient__category", "category_override"
        )

        grouped_items = defaultdict(list)
        uncategorized = []

        for item in items:
            category = item.category
            if category:
                grouped_items[category].append(item)
            else:
                uncategorized.append(item)

        sorted_categories = sorted(grouped_items.keys(), key=lambda c: (c.sort_order, c.name))
        categorized_items = [(cat, grouped_items[cat]) for cat in sorted_categories]

        # Render items HTML
        items_html = render(
            request,
            "shopping/partials/items_list.html",
            {
                "shopping_list": shopping_list,
                "categorized_items": categorized_items,
                "uncategorized": uncategorized,
            },
        ).content.decode()

        # Render progress bar with OOB swap
        progress_html = render(
            request,
            "shopping/partials/progress_bar.html",
            {"shopping_list": shopping_list},
        ).content.decode()

        return HttpResponse(items_html + progress_html)

    messages.success(request, f"Removed {count} checked items.")
    return redirect("shopping:detail", pk=pk)


@login_required
@require_POST
def uncheck_all(request, pk):
    """Uncheck all items in a shopping list."""
    shopping_list = get_object_or_404(ShoppingList, pk=pk)
    shopping_list.items.update(checked=False)

    if request.headers.get("HX-Request"):
        # Re-fetch and group items for the response
        items = shopping_list.items.select_related(
            "ingredient", "ingredient__category", "category_override"
        )

        grouped_items = defaultdict(list)
        uncategorized = []

        for item in items:
            category = item.category
            if category:
                grouped_items[category].append(item)
            else:
                uncategorized.append(item)

        sorted_categories = sorted(grouped_items.keys(), key=lambda c: (c.sort_order, c.name))
        categorized_items = [(cat, grouped_items[cat]) for cat in sorted_categories]

        # Render items HTML
        items_html = render(
            request,
            "shopping/partials/items_list.html",
            {
                "shopping_list": shopping_list,
                "categorized_items": categorized_items,
                "uncategorized": uncategorized,
            },
        ).content.decode()

        # Render progress bar with OOB swap
        progress_html = render(
            request,
            "shopping/partials/progress_bar.html",
            {"shopping_list": shopping_list},
        ).content.decode()

        return HttpResponse(items_html + progress_html)

    return redirect("shopping:detail", pk=pk)
