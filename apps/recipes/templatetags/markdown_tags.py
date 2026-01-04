"""Template tags for markdown formatting."""

import re

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def preprocess_lists(text):
    """
    Pre-process text to help markdown recognize lists.

    Markdown requires a blank line before a list, and NO blank lines
    between list items. This function:
    1. Auto-numbers paragraph-style instructions that look like steps
    2. Removes blank lines between list items
    3. Merges continuation lines into their parent list item
    4. Adds a blank line before the list starts
    """
    lines = text.split("\n")

    # Pattern for numbered list items: "1.", "2)", "1:", etc.
    numbered_pattern = re.compile(r"^\s*\d+[\.\)\:]\s+")
    # Pattern for bullet list items
    bullet_pattern = re.compile(r"^\s*[-\*\+]\s+")

    # Check if text already has numbered lines
    has_numbers = any(numbered_pattern.match(line) for line in lines if line.strip())

    # If no numbers, check if it looks like step-by-step instructions
    # (multiple non-blank lines that could be individual steps)
    if not has_numbers:
        non_blank_lines = [line.strip() for line in lines if line.strip()]
        # Auto-number if we have 3+ separate paragraphs/lines that look like steps
        if len(non_blank_lines) >= 3:
            # Check they're not super long (would indicate a single paragraph)
            avg_length = sum(len(line) for line in non_blank_lines) / len(non_blank_lines)
            if avg_length < 500:  # Likely individual steps, not one long paragraph
                # Create numbered list without blank lines between items
                numbered_lines = [f"{i}. {line}" for i, line in enumerate(non_blank_lines, 1)]
                # Add blank line at start for markdown, then join without extra blanks
                return "\n" + "\n".join(numbered_lines)

    # For text that already has numbers, merge continuation lines and format
    result = []
    in_list = False
    prev_was_blank = True
    current_item = None

    for line in lines:
        is_numbered = numbered_pattern.match(line)
        is_bullet = bullet_pattern.match(line)
        is_list_item = is_numbered or is_bullet
        is_blank = line.strip() == ""

        if is_list_item:
            # Save previous item if exists
            if current_item is not None:
                result.append(current_item)

            # Add blank line before first list item if needed
            if not in_list and not prev_was_blank:
                result.append("")
            in_list = True

            # Normalize numbered list format to "1. " style
            if is_numbered:
                line = numbered_pattern.sub(
                    lambda m: re.sub(r"(\d+)[\.\)\:]", r"\1.", m.group()), line
                )
            current_item = line
        elif is_blank:
            # Blank line - save current item and reset
            if current_item is not None:
                result.append(current_item)
                current_item = None
            # Skip blank lines within a list
            if not in_list:
                result.append(line)
        else:
            # Non-list, non-blank line
            if in_list and current_item is not None:
                # Continuation of previous list item - append to it
                current_item += " " + line.strip()
            else:
                # Regular paragraph - end any current list
                if current_item is not None:
                    result.append(current_item)
                    current_item = None
                if in_list:
                    result.append("")  # Add blank after list ends
                in_list = False
                result.append(line)

        prev_was_blank = is_blank

    # Don't forget the last item
    if current_item is not None:
        result.append(current_item)

    return "\n".join(result)


@register.filter(name="markdown")
def markdown_format(value):
    """
    Convert markdown text to HTML.

    Supports:
    - Numbered and bulleted lists
    - Bold (**text** or __text__)
    - Italic (*text* or _text_)
    - Line breaks
    - Paragraphs
    """
    if not value:
        return ""

    # Pre-process to help markdown recognize lists
    value = preprocess_lists(value)

    # Configure markdown with extensions for better list handling
    md = markdown.Markdown(
        extensions=[
            "nl2br",  # Convert newlines to <br>
            "sane_lists",  # Better list handling
        ]
    )

    html = md.convert(value)
    return mark_safe(html)
