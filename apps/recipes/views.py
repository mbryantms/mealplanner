from decimal import Decimal

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import (
    CategoryQuickForm,
    IngredientQuickForm,
    RecipeForm,
    RecipeIngredientForm,
    RecipeSearchForm,
    TagQuickForm,
)
from .models import Category, Ingredient, Recipe, RecipeIngredient, Tag


def recipe_list(request):
    """List all recipes with search and filter."""
    recipes = Recipe.objects.select_related("category").prefetch_related("tags")

    # Search
    search_query = request.GET.get("q", "").strip()
    if search_query:
        recipes = recipes.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(ingredients__name__icontains=search_query)
        ).distinct()

    # Filter by category
    category_id = request.GET.get("category")
    if category_id:
        recipes = recipes.filter(category_id=category_id)

    # Filter by tag
    tag_id = request.GET.get("tag")
    if tag_id:
        recipes = recipes.filter(tags__id=tag_id)

    # Pagination
    paginator = Paginator(recipes, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Search form
    form = RecipeSearchForm(request.GET)

    context = {
        "page_obj": page_obj,
        "form": form,
        "search_query": search_query,
    }

    # Return partial for HTMX requests
    if request.headers.get("HX-Request"):
        return render(request, "recipes/partials/recipe_list.html", context)

    return render(request, "recipes/recipe_list.html", context)


def recipe_detail(request, pk):
    """Display recipe details with optional scaling."""
    recipe = get_object_or_404(
        Recipe.objects.select_related("category").prefetch_related(
            "tags", "recipe_ingredients__ingredient"
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


def recipe_create(request):
    """Create a new recipe."""
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save()
            messages.success(request, f'Recipe "{recipe.name}" created successfully!')
            return redirect("recipes:recipe_detail", pk=recipe.pk)
    else:
        form = RecipeForm()

    context = {
        "form": form,
        "title": "Create Recipe",
        "submit_text": "Create Recipe",
    }
    return render(request, "recipes/recipe_form.html", context)


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


@require_POST
def ingredient_create_inline(request):
    """Create a new ingredient inline via HTMX."""
    form = IngredientQuickForm(request.POST)
    if form.is_valid():
        ingredient = form.save()
        # Return the new ingredient as an option
        return render(
            request,
            "recipes/partials/ingredient_option.html",
            {"ingredient": ingredient, "selected": True},
        )

    return render(
        request,
        "recipes/partials/ingredient_quick_form.html",
        {"form": form},
    )


@require_POST
def category_create_inline(request):
    """Create a new category inline via HTMX."""
    form = CategoryQuickForm(request.POST)
    if form.is_valid():
        category = form.save()
        return render(
            request,
            "recipes/partials/category_option.html",
            {"category": category, "selected": True},
        )

    return render(
        request,
        "recipes/partials/category_quick_form.html",
        {"form": form},
    )


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

    # Return form with errors
    return render(
        request,
        "recipes/partials/recipe_ingredient_form.html",
        {"form": form, "recipe": recipe},
    )


@require_POST
def recipe_ingredient_remove(request, pk):
    """Remove an ingredient from a recipe via HTMX."""
    recipe_ingredient = get_object_or_404(RecipeIngredient, pk=pk)
    recipe_ingredient.delete()
    return HttpResponse("")


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
