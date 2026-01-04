"""Template tags for markdown formatting."""

import re

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def preprocess_lists(text):
    """
    Pre-process text to help markdown recognize lists.

    Markdown requires a blank line before a list. This function:
    1. Adds blank lines before numbered/bullet lists that don't have them
    2. Auto-numbers paragraph-style instructions that look like steps
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
        non_blank_lines = [line for line in lines if line.strip()]
        # Auto-number if we have 3+ separate lines that look like steps
        if len(non_blank_lines) >= 3:
            # Check they're not already a paragraph (very long lines)
            avg_length = sum(len(line) for line in non_blank_lines) / len(non_blank_lines)
            if avg_length < 300:  # Likely individual steps, not paragraphs
                numbered_lines = []
                step_num = 1
                for line in lines:
                    if line.strip():
                        numbered_lines.append(f"{step_num}. {line.strip()}")
                        step_num += 1
                    else:
                        numbered_lines.append(line)
                lines = numbered_lines
                has_numbers = True

    # Now process for markdown list formatting
    result = []
    prev_was_list = False
    prev_was_blank = True  # Treat start as blank

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
