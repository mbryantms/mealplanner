"""Text parsing service for recipe import."""

import re
from dataclasses import dataclass


class RecipeParsingError(Exception):
    """Raised when recipe text cannot be parsed."""

    pass


@dataclass
class ParsedIngredient:
    """Represents a parsed ingredient line."""

    raw_text: str
    quantity: str | None
    unit: str | None
    name: str
    preparation: str | None


def parse_recipe_text(raw_text: str) -> dict:
    """
    Parse unstructured recipe text into structured fields.

    Expected format (flexible):
    - Title on first non-empty line
    - "Ingredients:" section followed by ingredient list
    - "Instructions:" or "Directions:" section followed by steps
    - Optional: prep/cook time, servings

    Returns dict with keys:
    - name, description, instructions, ingredients (list of ParsedIngredient)
    - prep_time, cook_time (int minutes or None)
    - servings (int or None)
    """
    lines = [line.strip() for line in raw_text.strip().split("\n")]
    lines = [line for line in lines if line]  # Remove empty lines

    if not lines:
        raise RecipeParsingError("No text provided")

    result = {
        "name": "",
        "description": "",
        "instructions": "",
        "ingredients": [],
        "prep_time": None,
        "cook_time": None,
        "servings": None,
    }

    # Parse title (first line before any section header)
    result["name"] = lines[0]

    # Find section boundaries
    ingredients_start = _find_section(lines, ["ingredients", "what you need", "you will need"])
    instructions_start = _find_section(
        lines, ["instructions", "directions", "method", "steps", "preparation"]
    )

    # Extract ingredients
    if ingredients_start is not None:
        end = instructions_start if instructions_start else len(lines)
        ingredient_lines = lines[ingredients_start + 1 : end]
        result["ingredients"] = [
            parse_ingredient_line(line)
            for line in ingredient_lines
            if _is_ingredient_line(line)
        ]

    # Extract instructions
    if instructions_start is not None:
        instruction_lines = lines[instructions_start + 1 :]
        # Filter out any lines that look like metadata
        instruction_lines = [
            line for line in instruction_lines if not _is_metadata_line(line)
        ]
        result["instructions"] = "\n".join(instruction_lines)

    # Extract times and servings from header area
    header_end = ingredients_start if ingredients_start else len(lines)
    header_text = " ".join(lines[: min(10, header_end)])
    result["prep_time"] = _extract_time(header_text, ["prep", "preparation"])
    result["cook_time"] = _extract_time(header_text, ["cook", "cooking"])
    result["servings"] = _extract_servings(header_text)

    # If no ingredients section found, try to find ingredient-like lines anywhere
    if not result["ingredients"]:
        for line in lines[1:]:  # Skip title
            if _looks_like_ingredient(line):
                result["ingredients"].append(parse_ingredient_line(line))

    return result


def parse_ingredient_line(line: str) -> ParsedIngredient:
    """
    Parse a single ingredient line into components.

    Examples:
    - "2 cups flour" -> qty=2, unit=cups, name=flour
    - "1/2 lb chicken breast, diced" -> qty=1/2, unit=lb, name=chicken breast, prep=diced
    - "salt to taste" -> qty=None, unit=None, name=salt to taste
    """
    original_line = line

    # Clean the line
    line = re.sub(r"^[-*•◦▪▸►]\s*", "", line)  # Remove bullet points
    line = re.sub(r"^\d+\.\s*", "", line)  # Remove numbered list markers

    # Common units for matching
    units = (
        r"cups?|tbsps?|tsps?|tablespoons?|teaspoons?|oz|ounces?|lbs?|pounds?|"
        r"g|grams?|kg|kilograms?|ml|milliliters?|l|liters?|"
        r"cloves?|cans?|packages?|pkgs?|pinch(?:es)?|bunch(?:es)?|"
        r"heads?|stalks?|pieces?|pcs?|slices?|sticks?|"
        r"large|medium|small|whole|"
        r"sprigs?|leaves?|handfuls?"
    )

    # Patterns for quantity
    # Match fractions (1/2, 1 1/2), decimals (1.5), ranges (1-2), or plain numbers
    qty_pattern = r"^(\d+(?:\s+\d+)?(?:[/\.]\d+)?(?:\s*-\s*\d+(?:[/\.]\d+)?)?)\s*"

    quantity = None
    unit = None
    preparation = None

    # Extract quantity
    qty_match = re.match(qty_pattern, line, re.IGNORECASE)
    if qty_match:
        quantity = qty_match.group(1).strip()
        line = line[qty_match.end() :]

    # Extract unit
    unit_pattern = rf"^({units})\s+"
    unit_match = re.match(unit_pattern, line, re.IGNORECASE)
    if unit_match:
        unit = unit_match.group(1).lower()
        line = line[unit_match.end() :]

    # Extract preparation (after comma or in parentheses)
    # Check for parenthetical preparation first
    paren_match = re.search(r"\(([^)]+)\)\s*$", line)
    if paren_match:
        preparation = paren_match.group(1).strip()
        line = line[: paren_match.start()].strip()

    # Check for preparation after comma
    if not preparation:
        comma_match = re.search(r",\s*([\w\s]+)$", line)
        if comma_match:
            prep_text = comma_match.group(1).strip()
            # Only treat as preparation if it looks like one
            prep_words = [
                "diced",
                "chopped",
                "minced",
                "sliced",
                "cubed",
                "crushed",
                "grated",
                "shredded",
                "julienned",
                "melted",
                "softened",
                "divided",
                "optional",
                "to taste",
                "for garnish",
                "peeled",
                "seeded",
                "cored",
                "trimmed",
                "halved",
                "quartered",
            ]
            if any(pw in prep_text.lower() for pw in prep_words):
                preparation = prep_text
                line = line[: comma_match.start()].strip()

    return ParsedIngredient(
        raw_text=original_line,
        quantity=quantity,
        unit=unit,
        name=line.strip(),
        preparation=preparation,
    )


def _find_section(lines: list[str], keywords: list[str]) -> int | None:
    """Find line index where a section starts."""
    for i, line in enumerate(lines):
        lower = line.lower().rstrip(":").strip()
        if any(kw == lower or lower.startswith(kw + ":") for kw in keywords):
            return i
    return None


def _is_ingredient_line(line: str) -> bool:
    """Check if line looks like an ingredient (not a section header)."""
    lower = line.lower().rstrip(":").strip()
    headers = [
        "instructions",
        "directions",
        "method",
        "steps",
        "notes",
        "tips",
        "preparation",
        "ingredients",
    ]
    if any(h == lower for h in headers):
        return False
    return len(line) > 2


def _is_metadata_line(line: str) -> bool:
    """Check if line looks like metadata (time, servings, etc.)."""
    lower = line.lower()
    metadata_patterns = [
        r"prep\s*time",
        r"cook\s*time",
        r"total\s*time",
        r"serves?\s*\d",
        r"servings?\s*:",
        r"yield\s*:",
        r"makes?\s*\d",
    ]
    return any(re.search(pat, lower) for pat in metadata_patterns)


def _looks_like_ingredient(line: str) -> bool:
    """Check if a line looks like an ingredient."""
    # Has a quantity at the start
    if re.match(r"^\d", line):
        return True
    # Starts with a bullet
    if re.match(r"^[-*•]", line):
        return True
    return False


def _extract_time(text: str, keywords: list[str]) -> int | None:
    """Extract time in minutes from text near keywords."""
    for kw in keywords:
        # Try various patterns
        patterns = [
            rf"{kw}\s*(?:time)?[\s:]*(\d+)\s*(?:minutes?|mins?|m)\b",
            rf"{kw}\s*(?:time)?[\s:]*(\d+)\s*(?:hours?|hrs?|h)\b",
            rf"(\d+)\s*(?:minutes?|mins?|m)\s*{kw}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = int(match.group(1))
                # Check if it's hours
                if "hour" in pattern or "hrs" in pattern or "h)" in pattern:
                    value *= 60
                return value
    return None


def _extract_servings(text: str) -> int | None:
    """Extract servings number from text."""
    patterns = [
        r"(?:serves?|servings?|yield|makes?)\s*[:\s]*(\d+)",
        r"(\d+)\s*(?:servings?|portions?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None
