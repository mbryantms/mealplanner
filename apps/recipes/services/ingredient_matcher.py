"""Ingredient matching service for recipe import."""

from dataclasses import dataclass
from difflib import SequenceMatcher

from django.db.models import Q

from apps.recipes.models import Ingredient

from .text_parser import ParsedIngredient


@dataclass
class IngredientMatch:
    """Represents a matched ingredient with confidence score."""

    raw_text: str
    parsed_quantity: str | None
    parsed_unit: str | None
    parsed_name: str
    parsed_preparation: str | None
    matched_ingredient: Ingredient | None
    match_confidence: float  # 0.0 to 1.0
    suggested_ingredients: list[Ingredient]
    needs_creation: bool


def match_ingredients(parsed_ingredients: list[ParsedIngredient]) -> list[IngredientMatch]:
    """
    Match parsed ingredient strings to existing Ingredient records.

    Strategy:
    1. Exact name match (case-insensitive)
    2. Fuzzy match using sequence matching
    3. Partial match (ingredient name contains or is contained by)
    4. Return suggestions for user review
    """
    results = []

    for parsed in parsed_ingredients:
        name = parsed.name if hasattr(parsed, "name") else str(parsed)
        name_clean = _clean_ingredient_name(name)

        # Try exact match first
        exact = Ingredient.objects.filter(name__iexact=name_clean).first()
        if exact:
            results.append(
                IngredientMatch(
                    raw_text=parsed.raw_text,
                    parsed_quantity=parsed.quantity,
                    parsed_unit=parsed.unit,
                    parsed_name=name,
                    parsed_preparation=parsed.preparation,
                    matched_ingredient=exact,
                    match_confidence=1.0,
                    suggested_ingredients=[exact],
                    needs_creation=False,
                )
            )
            continue

        # Fuzzy search - get candidates
        candidates = list(
            Ingredient.objects.filter(
                Q(name__icontains=name_clean) | Q(name__in=_get_partial_terms(name_clean))
            )[:20]
        )

        # If no candidates from partial match, get all ingredients for fuzzy matching
        if not candidates:
            candidates = list(Ingredient.objects.all()[:100])

        # Score candidates using fuzzy matching
        scored = []
        for ingredient in candidates:
            # Compare both the full name and individual words
            score1 = SequenceMatcher(None, name_clean.lower(), ingredient.name.lower()).ratio()

            # Also check if key words match
            name_words = set(name_clean.lower().split())
            ing_words = set(ingredient.name.lower().split())
            common_words = name_words & ing_words
            word_score = len(common_words) / max(len(name_words), 1)

            # Combined score
            score = max(score1, word_score * 0.9)
            scored.append((ingredient, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        top_matches = scored[:5]

        best_match = top_matches[0] if top_matches else (None, 0.0)

        # Determine if we have a confident match
        confidence_threshold = 0.7
        matched = best_match[0] if best_match[1] >= confidence_threshold else None

        results.append(
            IngredientMatch(
                raw_text=parsed.raw_text,
                parsed_quantity=parsed.quantity,
                parsed_unit=parsed.unit,
                parsed_name=name,
                parsed_preparation=parsed.preparation,
                matched_ingredient=matched,
                match_confidence=best_match[1] if best_match[0] else 0.0,
                suggested_ingredients=[i for i, s in top_matches if s > 0.3],
                needs_creation=matched is None,
            )
        )

    return results


def _clean_ingredient_name(name: str) -> str:
    """Clean an ingredient name for matching."""
    # Remove common modifiers that don't affect the ingredient itself
    modifiers = [
        "fresh",
        "dried",
        "frozen",
        "organic",
        "large",
        "small",
        "medium",
        "ripe",
        "raw",
        "cooked",
        "canned",
        "whole",
        "ground",
        "extra-virgin",
        "extra virgin",
        "low-sodium",
        "unsalted",
        "salted",
    ]

    name_lower = name.lower().strip()

    # Remove modifiers from the beginning
    for mod in modifiers:
        if name_lower.startswith(mod + " "):
            name_lower = name_lower[len(mod) + 1 :]

    return name_lower.strip()


def _get_partial_terms(name: str) -> list[str]:
    """Get individual words that might match ingredients."""
    # Common words to skip
    skip = {
        "fresh",
        "dried",
        "frozen",
        "organic",
        "large",
        "small",
        "medium",
        "the",
        "a",
        "an",
        "of",
        "for",
        "to",
    }

    words = name.lower().split()
    return [w for w in words if w not in skip and len(w) > 2]


def search_ingredients(query: str, limit: int = 10) -> list[Ingredient]:
    """Search for ingredients by name."""
    if len(query) < 2:
        return []

    return list(
        Ingredient.objects.filter(name__icontains=query).order_by("name")[:limit]
    )
