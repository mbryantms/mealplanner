"""Template tags for markdown formatting."""

import re

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def preprocess_lists(text):
    """
    Pre-process text to help markdown recognize lists.

    Markdown requires a blank line before a list. This function adds
    blank lines before numbered lists and bullet lists that don't have them.
    """
    lines = text.split("\n")
    result = []
    prev_was_list = False
    prev_was_blank = True  # Treat start as blank

    # Pattern for numbered list items: "1.", "2)", "1:", etc.
    numbered_pattern = re.compile(r"^\s*\d+[\.\)\:]\s+")
    # Pattern for bullet list items
    bullet_pattern = re.compile(r"^\s*[-\*\+]\s+")

    for line in lines:
        is_numbered = numbered_pattern.match(line)
        is_bullet = bullet_pattern.match(line)
        is_list_item = is_numbered or is_bullet
        is_blank = line.strip() == ""

        # Add blank line before first list item if needed
        if is_list_item and not prev_was_list and not prev_was_blank:
            result.append("")

        # Normalize numbered list format to "1. " style for markdown
        if is_numbered:
            line = numbered_pattern.sub(
                lambda m: re.sub(r"(\d+)[\.\)\:]", r"\1.", m.group()), line
            )

        result.append(line)
        prev_was_list = is_list_item
        prev_was_blank = is_blank

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
