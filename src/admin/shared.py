from django.utils.html import format_html
from src.admin.base import * #noqa: F401

def format_strong(text):
    return format_html("<strong>{}</strong>", text)


def format_strong_with_subtext(primary, secondary, secondary_color="#888"):
    return format_html(
        "<strong>{}</strong><br><small style='color: {};'>{}</small>",
        primary,
        secondary_color,
        secondary if secondary else "—",
    )


def format_placeholder(value=None, placeholder="—", color="#888"):
    return (
        value
        if value
        else format_html("<span style='color:{};'>{}</span>", color, placeholder)
    )


def format_badge(label, background="#333", text_color="white"):
    return format_html(
        "<span style='background:{}; color:{}; padding:3px 8px; border-radius:6px; font-size:12px;'>{}</span>",
        background,
        text_color,
        label,
    )


def format_currency(amount):
    return format_html("<b>${:,.2f}</b>", amount) if amount is not None else "—"


def format_boolean_icon(
    flag, true_icon="✅", false_icon="❌", true_color="#28a745", false_color="#999"
):
    color = true_color if flag else false_color
    icon = true_icon if flag else false_icon
    return format_html(
        "<span style='color:{}; font-size:14px;'>{}</span>",
        color,
        icon,
    )


def format_link(url, label=None):
    return (
        format_html("<a href='{}' target='_blank'>{}</a>", url, label or url)
        if url
        else format_placeholder()
    )