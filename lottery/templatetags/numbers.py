from django.template import Library
from babel.numbers import format_currency, format_decimal
register = Library()


@register.filter
def currency(value):
    return format_currency(value, 'R$', locale='pt_br')


@register.filter
def decimal(value):
    return format_decimal(value, locale='pt_br')