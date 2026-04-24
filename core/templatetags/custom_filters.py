from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acceder a un valor de diccionario en las plantillas."""
    return dictionary.get(key)
