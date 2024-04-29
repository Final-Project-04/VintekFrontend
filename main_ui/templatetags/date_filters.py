from django import template
from datetime import datetime

register = template.Library()

@register.filter
def format_timestamp(value):
    timestamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')