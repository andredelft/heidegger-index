from unidecode import unidecode
import re
from fuzzysearch import find_near_matches

from django.template.defaultfilters import slugify as _slugify

PREFIXES = ["der", "die", "das", "den"]

PREFIX_FILTER = re.compile(rf'^(?:{"|".join(PREFIXES)})\s+')


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


def match_lemmata(search_term, index, max_l_dist=2, include_search_term=True):

    key_to_lemma = {gen_sort_key(lemma): lemma for lemma in index.keys()}
    keys = key_to_lemma.keys()

    if not include_search_term:
        # Remove subject lemma from list
        keys = [k for k in keys if k != gen_sort_key(search_term)]

    matches = [
        (
            key_to_lemma[key],
            find_near_matches(
                gen_sort_key(search_term),
                key,
                max_l_dist=max_l_dist,
            ),
        )
        for key in keys
    ]

    # Remove unmatched lemmata from list
    matches = [m for m in matches if m[1]]

    # Sort by levensteihn distance first, then by lemma
    matches.sort(key=lambda match: (min(m.dist for m in match[1]), match[0]))

    return matches


def slugify(value):
    """Slugify function extended with `unidecode` for better unicode representation"""
    return _slugify(unidecode(value))
