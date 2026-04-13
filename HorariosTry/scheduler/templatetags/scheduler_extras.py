from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Devuelve el valor del diccionario para la clave dada (la clave puede ser una tupla)."""
    return dictionary.get(key)