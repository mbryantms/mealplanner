from decimal import Decimal

from django import template

register = template.Library()

# Mapping of singular units to their plural forms
# Units not in this dict will have 's' appended (standard English pluralization)
UNIT_PLURALS = {
    # Volume - standard
    "cup": "cups",
    "tablespoon": "tablespoons",
    "tbsp": "tbsp",
    "teaspoon": "teaspoons",
    "tsp": "tsp",
    "fluid ounce": "fluid ounces",
    "fl oz": "fl oz",
    "pint": "pints",
    "quart": "quarts",
    "gallon": "gallons",
    "liter": "liters",
    "litre": "litres",
    "milliliter": "milliliters",
    "ml": "ml",
    # Weight
    "ounce": "ounces",
    "oz": "oz",
    "pound": "pounds",
    "lb": "lbs",
    "gram": "grams",
    "g": "g",
    "kilogram": "kilograms",
    "kg": "kg",
    # Count/pieces
    "piece": "pieces",
    "slice": "slices",
    "clove": "cloves",
    "head": "heads",
    "bunch": "bunches",
    "sprig": "sprigs",
    "stalk": "stalks",
    "strip": "strips",
    "leaf": "leaves",
    "can": "cans",
    "jar": "jars",
    "package": "packages",
    "bag": "bags",
    "box": "boxes",
    "bottle": "bottles",
    "stick": "sticks",
    "cube": "cubes",
    "drop": "drops",
    # Small amounts
    "pinch": "pinches",
    "dash": "dashes",
    "handful": "handfuls",
    # Other common units
    "serving": "servings",
    "portion": "portions",
    "scoop": "scoops",
    "ear": "ears",
    "rib": "ribs",
    "fillet": "fillets",
    "breast": "breasts",
    "thigh": "thighs",
    "drumstick": "drumsticks",
    "wing": "wings",
    "patty": "patties",
    "link": "links",
    "rasher": "rashers",
}

# Build reverse mapping for plural -> singular
UNIT_SINGULARS = {v: k for k, v in UNIT_PLURALS.items()}


@register.filter
def pluralize_unit(unit, quantity):
    """
    Pluralize a unit based on quantity.

    Usage: {{ item.unit|pluralize_unit:item.quantity }}

    Returns the plural form if quantity > 1, singular otherwise.
    Handles common cooking units with irregular plurals.
    """
    if not unit:
        return ""

    # Convert quantity to a number for comparison
    try:
        if isinstance(quantity, (int, float, Decimal)):
            qty = float(quantity)
        elif quantity:
            qty = float(quantity)
        else:
            qty = 1  # Default to singular if no quantity
    except (ValueError, TypeError):
        qty = 1

    unit_lower = unit.lower().strip()

    # Determine if we need singular or plural
    needs_plural = qty > 1

    if needs_plural:
        # Check if already plural
        if unit_lower in UNIT_SINGULARS:
            return unit  # Already plural, return as-is
        # Look up plural form
        if unit_lower in UNIT_PLURALS:
            plural = UNIT_PLURALS[unit_lower]
            # Preserve original capitalization
            if unit[0].isupper():
                return plural.capitalize()
            return plural
        # Default: add 's' if not already ending in 's'
        if not unit_lower.endswith("s"):
            return unit + "s"
        return unit
    else:
        # Check if already singular
        if unit_lower in UNIT_PLURALS:
            return unit  # Already singular, return as-is
        # Look up singular form
        if unit_lower in UNIT_SINGULARS:
            singular = UNIT_SINGULARS[unit_lower]
            # Preserve original capitalization
            if unit[0].isupper():
                return singular.capitalize()
            return singular
        # Default: return as-is for singular
        return unit
