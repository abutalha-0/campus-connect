from django.utils.html import format_html


def thumbnail(url, size=40):
    """Small image preview for admin list/detail displays. Returns an em-dash
    when there's no image, so admins can tell "no photo" from "not loaded"."""
    if not url:
        return "—"
    return format_html(
        '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:6px;" />',
        url, size, size,
    )
