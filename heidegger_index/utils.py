from unidecode import unidecode
import re
import yaml
from fuzzysearch import find_near_matches

from django.template.defaultfilters import slugify as _slugify
from django.conf import settings


PREFIXES = ["der", "die", "das", "den"]

PREFIX_FILTER = re.compile(fr'^(?:{"|".join(PREFIXES)})\s+')

INDEX_FILE = settings.BASE_DIR / "index" / "heidegger-index.yml"


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

def match_lemmata(search_term, max_l_dist=2, num_results=5, include_search_term=True):

    with open(INDEX_FILE) as f:
        key_to_lemma = {
            gen_sort_key(lemma): lemma for lemma in yaml.load(f).keys()
        }
        keys = key_to_lemma.keys()

    if not include_search_term:
        # Remove subject lemma from list
        keys = [k for k in keys if k != gen_sort_key(search_term)]


    matches = [
        (key_to_lemma[key], find_near_matches(gen_sort_key(search_term), key, max_l_dist=max_l_dist))
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
