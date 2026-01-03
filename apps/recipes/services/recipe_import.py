"""Recipe import service for URL scraping."""

import logging
from io import BytesIO

import httpx
from django.core.files.base import ContentFile

from apps.recipes.models import Ingredient, Recipe, RecipeIngredient

from .ingredient_matcher import IngredientMatch
from .text_parser import ParsedIngredient

logger = logging.getLogger(__name__)


class RecipeScrapingError(Exception):
    """Raised when recipe scraping fails."""

    pass


# URLs we should not fetch (security)
BLOCKED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "::1", "169.254.169.254"]


def scrape_recipe_from_url(url: str) -> dict:
    """
    Scrape recipe data from a URL using recipe-scrapers library.

    Returns dict with keys:
    - name, description, instructions, ingredients (list of strings)
    - prep_time, cook_time, total_time (int minutes or None)
    - servings (int or None), image_url, source_url
    """
    try:
        from recipe_scrapers import scrape_html
        from recipe_scrapers._exceptions import WebsiteNotImplementedError
    except ImportError:
        raise RecipeScrapingError(
            "recipe-scrapers library is not installed. "
            "Please run: uv add recipe-scrapers httpx"
        )

    # Validate URL
    from urllib.parse import urlparse

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise RecipeScrapingError("Invalid URL format.")

    if parsed.hostname in BLOCKED_HOSTS:
        raise RecipeScrapingError("This URL is not allowed.")

    try:
        # Fetch HTML with httpx
        response = httpx.get(
            url,
            follow_redirects=True,
            timeout=15.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()
        html = response.text

        # Parse with recipe-scrapers in wild mode
        scraper = scrape_html(html, org_url=url, wild_mode=True)

        return {
            "name": scraper.title(),
            "description": _safe_call(scraper.description) or "",
            "instructions": scraper.instructions() or "",
            "instructions_list": _safe_call(scraper.instructions_list) or [],
            "ingredients": scraper.ingredients() or [],
            "prep_time": _safe_call(scraper.prep_time),
            "cook_time": _safe_call(scraper.cook_time),
            "total_time": _safe_call(scraper.total_time),
            "servings": _parse_servings(_safe_call(scraper.yields)),
            "image_url": _safe_call(scraper.image),
            "source_url": url,
        }
    except httpx.HTTPError as e:
        logger.warning(f"HTTP error scraping {url}: {e}")
        raise RecipeScrapingError(f"Failed to fetch URL: {e}")
    except WebsiteNotImplementedError:
        raise RecipeScrapingError(
            "This website is not directly supported. "
            "Try using the 'Paste Text' option instead."
        )
    except Exception as e:
        logger.warning(f"Error scraping {url}: {e}")
        raise RecipeScrapingError(f"Failed to parse recipe: {e}")


def _safe_call(method):
    """Safely call a scraper method that might raise an exception."""
    try:
        result = method()
        return result if result else None
    except Exception:
        return None


def _parse_servings(yields_str: str | None) -> int | None:
    """Extract numeric servings from yields string like '4 servings'."""
    if not yields_str:
        return None
    import re

    match = re.search(r"(\d+)", yields_str)
    return int(match.group(1)) if match else None


def download_recipe_image(image_url: str, recipe: Recipe) -> bool:
    """
    Download and attach image to recipe.

    Returns True if successful, False otherwise.
    """
    if not image_url:
        return False

    try:
        response = httpx.get(
            image_url,
            follow_redirects=True,
            timeout=15.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
        response.raise_for_status()

        # Validate content type
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            logger.warning(f"Invalid content type for image: {content_type}")
            return False

        # Determine file extension
        ext = "jpg"
        if "png" in content_type:
            ext = "png"
        elif "gif" in content_type:
            ext = "gif"
        elif "webp" in content_type:
            ext = "webp"

        # Save to recipe
        filename = f"imported_{recipe.pk}.{ext}"
        recipe.image.save(filename, ContentFile(response.content), save=True)

        logger.info(f"Downloaded image for recipe {recipe.pk}")
        return True

    except Exception as e:
        logger.warning(f"Failed to download image from {image_url}: {e}")
        return False


def create_recipe_from_import(
    name: str,
    description: str,
    instructions: str,
    prep_time: int | None,
    cook_time: int | None,
    servings: int,
    source_url: str,
    ingredients: list[dict],
    image_url: str | None = None,
) -> Recipe:
    """
    Create a new Recipe from import data.

    ingredients is a list of dicts with keys:
    - ingredient_id: int (existing ingredient) or None
    - create_name: str (name for new ingredient) or None
    - quantity: str or None
    - unit: str or None
    - preparation: str or None
    """
    # Create the recipe
    recipe = Recipe.objects.create(
        name=name,
        description=description,
        instructions=instructions,
        prep_time=prep_time,
        cook_time=cook_time,
        servings=servings or 4,
        source_url=source_url or "",
    )

    # Add ingredients
    for idx, ing_data in enumerate(ingredients):
        ingredient = None

        if ing_data.get("ingredient_id"):
            ingredient = Ingredient.objects.filter(pk=ing_data["ingredient_id"]).first()

        if not ingredient and ing_data.get("create_name"):
            # Create new ingredient
            ingredient = Ingredient.objects.create(
                name=ing_data["create_name"].strip().title(),
                default_unit=ing_data.get("unit") or "",
            )

        if ingredient:
            # Parse quantity
            quantity = None
            if ing_data.get("quantity"):
                try:
                    # Handle fractions like "1/2" or "1 1/2"
                    qty_str = ing_data["quantity"]
                    if " " in qty_str and "/" in qty_str:
                        # Mixed number like "1 1/2"
                        parts = qty_str.split(" ", 1)
                        whole = float(parts[0])
                        frac_parts = parts[1].split("/")
                        fraction = float(frac_parts[0]) / float(frac_parts[1])
                        quantity = whole + fraction
                    elif "/" in qty_str:
                        # Simple fraction like "1/2"
                        parts = qty_str.split("/")
                        quantity = float(parts[0]) / float(parts[1])
                    else:
                        quantity = float(qty_str)
                except (ValueError, ZeroDivisionError, IndexError):
                    pass

            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                quantity=quantity,
                unit=ing_data.get("unit") or "",
                preparation=ing_data.get("preparation") or "",
                order=idx,
            )

    # Download image if provided
    if image_url:
        download_recipe_image(image_url, recipe)

    return recipe
