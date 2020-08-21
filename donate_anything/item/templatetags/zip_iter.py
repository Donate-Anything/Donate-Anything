from typing import Iterable

from django import template


register = template.Library()


@register.filter(name="zip")
def zip_iter(a: Iterable, b: Iterable):
    return zip(a, b)
