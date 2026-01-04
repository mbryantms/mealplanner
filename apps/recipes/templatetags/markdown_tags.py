"""Template tags for markdown formatting."""

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


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

    # Configure markdown with extensions for better list handling
    md = markdown.Markdown(
        extensions=[
            "nl2br",  # Convert newlines to <br>
            "sane_lists",  # Better list handling
        ]
    )

    html = md.convert(value)
    return mark_safe(html)
