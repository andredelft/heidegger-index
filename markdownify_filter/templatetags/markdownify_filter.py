import markdownify 

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter()
@stringfilter
def low(value):
	return value.lower()
