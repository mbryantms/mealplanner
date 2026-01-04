from datetime import date, datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.planning.models import MealPlan, MealType

from .forms import (
    IngredientQuickForm,
    RecipeForm,
    RecipeIngredientForm,
    RecipeSearchForm,
    TagQuickForm,
)
from .models import Ingredient, Recipe, RecipeIngredient, Tag


@login_required
def recipe_list(request):
    """List all recipes with search and filter."""
    recipes = Recipe.objects.prefetch_related("cuisines", "proteins", "dish_types", "tags")

    # Search
    search_query = request.GET.get("q", "").strip()
    if search_query:
        recipes = recipes.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(ingredients__name__icontains=search_query)
        ).distinct()

    # Filter by cuisines (AND logic)
    cuisine_ids = request.GET.getlist("cuisines")
    if cuisine_ids:
        for cuisine_id in cuisine_ids:
            recipes = recipes.filter(cuisines__id=cuisine_id)

    # Filter by proteins (AND logic)
    protein_ids = request.GET.getlist("proteins")
    if protein_ids:
        for protein_id in protein_ids:
            recipes = recipes.filter(proteins__id=protein_id)

    # Filter by dish types (AND logic)
    dish_type_ids = request.GET.getlist("dish_types")
    if dish_type_ids:
        for dish_type_id in dish_type_ids:
            recipes = recipes.filter(dish_types__id=dish_type_id)

    # Filter by tags (AND logic)
    tag_ids = request.GET.getlist("tags")
    if tag_ids:
        for tag_id in tag_ids:
            recipes = recipes.filter(tags__id=tag_id)

    # Pagination
    paginator = Paginator(recipes, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Search form with initial data
    form = RecipeSearchForm(request.GET)

    # Build query string for pagination (preserve filters)
    query_params = []
    if search_query:
        query_params.append(f"q={search_query}")
    for cuisine_id in cuisine_ids:
        query_params.append(f"cuisines={cuisine_id}")
    for protein_id in protein_ids:
        query_params.append(f"proteins={protein_id}")
    for dish_type_id in dish_type_ids:
        query_params.append(f"dish_types={dish_type_id}")
    for tag_id in tag_ids:
        query_params.append(f"tags={tag_id}")
    filter_query_string = "&".join(query_params)

    # Check if any filters are active
    has_filters = bool(cuisine_ids or protein_ids or dish_type_ids or tag_ids)

    context = {
        "page_obj": page_obj,
        "form": form,
        "search_query": search_query,
        "filter_query_string": filter_query_string,
        "cuisine_count": len(cuisine_ids),
        "protein_count": len(protein_ids),
        "dish_type_count": len(dish_type_ids),
        "tag_count": len(tag_ids),
        "has_filters": has_filters,
    }

    # Return partial for HTMX requests
    if request.headers.get("HX-Request"):
        return render(request, "recipes/partials/recipe_list_with_filters.html", context)

    return render(request, "recipes/recipe_list.html", context)


@login_required
def recipe_detail(request, pk):
    """Display recipe details with optional scaling."""
    recipe = get_object_or_404(
        Recipe.objects.prefetch_related(
            "cuisines", "proteins", "dish_types", "tags", "recipe_ingredients__ingredient"
        ),
        pk=pk,
    )

    # Get scaling factor from query params
    scale = request.GET.get("scale", "1")
    try:
        scale_factor = Decimal(scale)
        if scale_factor <= 0:
            scale_factor = Decimal("1")
    except (ValueError, TypeError):
        scale_factor = Decimal("1")

    # Calculate scaled servings
    scaled_servings = int(recipe.servings * scale_factor)

    # Scale ingredients
    scaled_ingredients = []
    for ri in recipe.recipe_ingredients.all():
        scaled_qty = ri.quantity * scale_factor if ri.quantity else None
        scaled_ingredients.append(
            {
                "ingredient": ri.ingredient,
                "quantity": scaled_qty,
                "unit": ri.unit or ri.ingredient.default_unit,
                "preparation": ri.preparation,
                "optional": ri.optional,
            }
        )

    context = {
        "recipe": recipe,
        "scale_factor": scale_factor,
        "scaled_servings": scaled_servings,
        "scaled_ingredients": scaled_ingredients,
        "scale_options": [
            ("0.5", "½×"),
            ("1", "1×"),
            ("1.5", "1½×"),
            ("2", "2×"),
            ("3", "3×"),
        ],
    }

    # Return partial for HTMX scaling requests
    if request.headers.get("HX-Request") and request.GET.get("scale"):
        return render(request, "recipes/partials/recipe_ingredients.html", context)

    return render(request, "recipes/recipe_detail.html", context)


@login_required
def recipe_create(request):
    """Create a new recipe."""
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save()
            messages.success(
                request,
                f'Recipe "{recipe.name}" created! Now add ingredients below.',
            )
            # Redirect to edit page so user can add ingredients
            return redirect("recipes:recipe_edit", pk=recipe.pk)
    else:
        form = RecipeForm()

    context = {
        "form": form,
        "title": "Create Recipe",
        "submit_text": "Create Recipe",
    }
    return render(request, "recipes/recipe_form.html", context)


@login_required
def recipe_edit(request, pk):
    """Edit an existing recipe."""
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            recipe = form.save()
            messages.success(request, f'Recipe "{recipe.name}" updated successfully!')
            return redirect("recipes:recipe_detail", pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)

    context = {
        "form": form,
        "recipe": recipe,
        "title": f"Edit {recipe.name}",
        "submit_text": "Save Changes",
    }
    return render(request, "recipes/recipe_form.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def recipe_delete(request, pk):
    """Delete a recipe."""
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == "POST":
        name = recipe.name
        recipe.delete()
        messages.success(request, f'Recipe "{name}" deleted.')
        return redirect("recipes:recipe_list")

    context = {"recipe": recipe}
    return render(request, "recipes/recipe_delete.html", context)


# HTMX Endpoints


@login_required
@require_GET
def ingredient_autocomplete(request):
    """Autocomplete endpoint for ingredients."""
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return HttpResponse("")

    ingredients = Ingredient.objects.filter(name__icontains=query)[:10]

    return render(
        request,
        "recipes/partials/ingredient_autocomplete.html",
        {"ingredients": ingredients, "query": query},
    )


@login_required
@require_http_methods(["GET", "POST"])
def ingredient_create_inline(request):
    """Create a new ingredient inline via HTMX."""
    if request.method == "POST":
        form = IngredientQuickForm(request.POST)
        if form.is_valid():
            ingredient = form.save()
            # Return the new ingredient as an option
            return render(
                request,
                "recipes/partials/ingredient_option.html",
                {"ingredient": ingredient, "selected": True},
            )
    else:
        # GET request - show form pre-filled with name if provided
        initial = {}
        if request.GET.get("name"):
            initial["name"] = request.GET["name"]
        form = IngredientQuickForm(initial=initial)

    return render(
        request,
        "recipes/partials/ingredient_quick_form.html",
        {"form": form},
    )


@login_required
@require_POST
def tag_create_inline(request):
    """Create a new tag inline via HTMX."""
    form = TagQuickForm(request.POST)
    if form.is_valid():
        tag = form.save()
        return render(
            request,
            "recipes/partials/tag_option.html",
            {"tag": tag},
        )

    return render(
        request,
        "recipes/partials/tag_quick_form.html",
        {"form": form},
    )


@login_required
@require_POST
def recipe_ingredient_add(request, pk):
    """Add an ingredient to a recipe via HTMX."""
    recipe = get_object_or_404(Recipe, pk=pk)
    form = RecipeIngredientForm(request.POST)

    if form.is_valid():
        recipe_ingredient = form.save(commit=False)
        recipe_ingredient.recipe = recipe
        # Set order to be last
        last_order = recipe.recipe_ingredients.count()
        recipe_ingredient.order = last_order
        recipe_ingredient.save()

        return render(
            request,
            "recipes/partials/recipe_ingredient_row.html",
            {"ri": recipe_ingredient, "recipe": recipe},
        )

    # Return form with errors - use OOB swap to replace in place
    return render(
        request,
        "recipes/partials/recipe_ingredient_form.html",
        {"form": form, "recipe": recipe, "show_errors": True},
    )


@login_required
@require_POST
def recipe_ingredient_remove(request, pk):
    """Remove an ingredient from a recipe via HTMX."""
    recipe_ingredient = get_object_or_404(RecipeIngredient, pk=pk)
    recipe_ingredient.delete()
    return HttpResponse("")


@login_required
@require_POST
def recipe_ingredient_update(request, pk):
    """Update a recipe ingredient via HTMX."""
    recipe_ingredient = get_object_or_404(RecipeIngredient, pk=pk)
    form = RecipeIngredientForm(request.POST, instance=recipe_ingredient)

    if form.is_valid():
        form.save()
        return render(
            request,
            "recipes/partials/recipe_ingredient_row.html",
            {"ri": recipe_ingredient, "recipe": recipe_ingredient.recipe},
        )

    return render(
        request,
        "recipes/partials/recipe_ingredient_edit_form.html",
        {"form": form, "ri": recipe_ingredient},
    )


@login_required
@require_GET
def add_to_meal_plan_modal(request, pk):
    """Show the 'Add to Meal Plan' modal for a recipe."""
    recipe = get_object_or_404(Recipe, pk=pk)

    context = {
        "recipe": recipe,
        "today": date.today().isoformat(),
    }

    return render(request, "recipes/partials/add_to_plan_modal.html", context)


@login_required
@require_POST
def add_to_meal_plan(request, pk):
    """Add a recipe to the meal plan."""
    recipe = get_object_or_404(Recipe, pk=pk)

    # Parse form data
    date_str = request.POST.get("date")
    meal_type = request.POST.get("meal_type")

    # Validate
    if not date_str:
        return render(
            request,
            "recipes/partials/add_to_plan_modal.html",
            {"recipe": recipe, "today": date.today().isoformat(), "error": "Please select a date."},
        )

    if not meal_type or meal_type not in [mt.value for mt in MealType]:
        return render(
            request,
            "recipes/partials/add_to_plan_modal.html",
            {"recipe": recipe, "today": date.today().isoformat(), "error": "Please select a meal type."},
        )

    try:
        plan_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return render(
            request,
            "recipes/partials/add_to_plan_modal.html",
            {"recipe": recipe, "today": date.today().isoformat(), "error": "Invalid date format."},
        )

    # Create the meal plan (multiple meals per slot allowed)
    meal_plan = MealPlan.objects.create(
        date=plan_date,
        meal_type=meal_type,
        recipe=recipe,
    )

    # Get the display name for meal type
    meal_type_display = dict(MealType.choices).get(meal_type, meal_type.title())

    return render(
        request,
        "recipes/partials/add_to_plan_success.html",
        {
            "recipe": recipe,
            "date": plan_date,
            "meal_type_display": meal_type_display,
        },
    )


# Recipe Import Views


@login_required
def recipe_import(request):
    """Main recipe import page with URL and text input options."""
    from .forms import RecipeTextImportForm, RecipeURLImportForm

    context = {
        "url_form": RecipeURLImportForm(),
        "text_form": RecipeTextImportForm(),
    }
    return render(request, "recipes/recipe_import.html", context)


@login_required
@require_POST
def recipe_import_from_url(request):
    """Scrape recipe from URL and return preview form."""
    import json

    from .forms import RecipeURLImportForm
    from .services.ingredient_matcher import match_ingredients
    from .services.recipe_import import RecipeScrapingError, scrape_recipe_from_url
    from .services.text_parser import ParsedIngredient

    form = RecipeURLImportForm(request.POST)
    if form.is_valid():
        url = form.cleaned_data["url"]
        try:
            recipe_data = scrape_recipe_from_url(url)

            # Parse ingredients from raw strings
            parsed_ingredients = []
            for ing_str in recipe_data.get("ingredients", []):
                from .services.text_parser import parse_ingredient_line

                parsed_ingredients.append(parse_ingredient_line(ing_str))

            # Match ingredients to existing
            matched_ingredients = match_ingredients(parsed_ingredients)

            # Get all ingredients for the selector
            all_ingredients = Ingredient.objects.all().order_by("name")

            return render(
                request,
                "recipes/partials/import_preview.html",
                {
                    "recipe_data": recipe_data,
                    "matched_ingredients": matched_ingredients,
                    "all_ingredients": all_ingredients,
                    "source_url": url,
                    "image_url": recipe_data.get("image_url"),
                },
            )
        except RecipeScrapingError as e:
            return render(
                request,
                "recipes/partials/import_error.html",
                {
                    "error": str(e),
                    "url": url,
                },
            )

    return render(
        request,
        "recipes/partials/import_error.html",
        {
            "error": "Invalid URL provided.",
        },
    )


@login_required
@require_POST
def recipe_import_from_text(request):
    """Parse pasted recipe text and return preview form."""
    from .forms import RecipeTextImportForm
    from .services.ingredient_matcher import match_ingredients
    from .services.text_parser import RecipeParsingError, parse_recipe_text

    form = RecipeTextImportForm(request.POST)
    if form.is_valid():
        raw_text = form.cleaned_data["recipe_text"]
        try:
            recipe_data = parse_recipe_text(raw_text)
            matched_ingredients = match_ingredients(recipe_data.get("ingredients", []))

            # Get all ingredients for the selector
            all_ingredients = Ingredient.objects.all().order_by("name")

            return render(
                request,
                "recipes/partials/import_preview.html",
                {
                    "recipe_data": recipe_data,
                    "matched_ingredients": matched_ingredients,
                    "all_ingredients": all_ingredients,
                    "source_url": "",
                    "image_url": None,
                },
            )
        except RecipeParsingError as e:
            return render(
                request,
                "recipes/partials/import_error.html",
                {
                    "error": str(e),
                },
            )

    return render(
        request,
        "recipes/partials/import_error.html",
        {
            "error": "Please provide recipe text.",
        },
    )


@login_required
@require_POST
def recipe_import_confirm(request):
    """Create recipe from confirmed import data."""
    import json

    from .services.recipe_import import create_recipe_from_import

    # Extract form data
    name = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()
    instructions = request.POST.get("instructions", "").strip()
    source_url = request.POST.get("source_url", "").strip()
    image_url = request.POST.get("image_url", "").strip()

    # Parse numeric fields
    prep_time = None
    cook_time = None
    servings = 4

    try:
        if request.POST.get("prep_time"):
            prep_time = int(request.POST.get("prep_time"))
    except (ValueError, TypeError):
        pass

    try:
        if request.POST.get("cook_time"):
            cook_time = int(request.POST.get("cook_time"))
    except (ValueError, TypeError):
        pass

    try:
        if request.POST.get("servings"):
            servings = int(request.POST.get("servings"))
    except (ValueError, TypeError):
        pass

    # Parse ingredients JSON
    ingredients = []
    ingredients_json = request.POST.get("ingredients_json", "[]")
    try:
        ingredients = json.loads(ingredients_json)
    except json.JSONDecodeError:
        pass

    # Validate required fields
    if not name:
        messages.error(request, "Recipe name is required.")
        return redirect("recipes:recipe_import")

    # Create the recipe
    recipe = create_recipe_from_import(
        name=name,
        description=description,
        instructions=instructions,
        prep_time=prep_time,
        cook_time=cook_time,
        servings=servings,
        source_url=source_url,
        ingredients=ingredients,
        image_url=image_url if image_url else None,
    )

    messages.success(request, f'Recipe "{recipe.name}" imported successfully!')
    return redirect("recipes:recipe_edit", pk=recipe.pk)
