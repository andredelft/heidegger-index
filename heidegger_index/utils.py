from unidecode import unidecode
import re

from django.template.defaultfilters import slugify as _slugify

PREFIXES = ["der", "die", "das", "den"]

PREFIX_FILTER = re.compile(fr'^(?:{"|".join(PREFIXES)})\s+')


def gen_sort_key(value):
    # Normalize unicode
    value = unidecode(value)
    # Convert to lowercase
    value = value.lower()
    # Filter some prefixes
    value, n = PREFIX_FILTER.subn("", value)
    while n:
        value, n = PREFIX_FILTER.subn("", value)
    return value


def slugify(value):
    """Slugify function extended with `unidecode` for better unicode representation"""
    return _slugify(unidecode(value))
