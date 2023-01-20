from unidecode import unidecode
import re
from fuzzysearch import find_near_matches

from django.template.defaultfilters import slugify as _slugify

PREFIXES = ["der", "die", "das", "den"]

PREFIX_FILTER = re.compile(rf'^(?:{"|".join(PREFIXES)})\s+')

REF_REGEX = re.compile(r"^(?P<start>\d+)(?:-(?P<end>\d+)|(?P<suffix>f{1,2})\.?)?$")


def gen_sort_key(value):
    # Strip surrounding whitespaces
    value = value.strip()
    # Normalize unicode
    value = unidecode(value)
    # Convert to lowercase
    value = value.lower()
    # Filter some prefixes
    value, n = PREFIX_FILTER.subn("", value)
    while n:
        value, n = PREFIX_FILTER.subn("", value)
    # Add leading zero's to numbers to improve number sorting
    value = re.sub("\d+", lambda m: f"{m.group():0>5}", value)
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


def contains_page(reference: dict, page: int) -> bool:

    if reference["end"]:
        if page >= reference["start"] and page <= reference["end"]:
            return True
    if not reference["end"] and reference["start"]:
        if page == reference["start"]:
            return True
        elif reference["suffix"] == "f" and page == reference["start"] + 1:
            return True
        elif reference["suffix"] == "ff" and page == reference["start"] + 2:
            return True

    return False


def contains_page_range(reference: dict, page_range) -> bool:
    if not type(page_range) == dict:
        page_range = re.fullmatch(REF_REGEX, page_range)

        if not page_range:
            raise ValueError("Not a valid page range given.")

    page_start = int(page_range["start"])

    if not page_range["end"] and page_range["suffix"]:
        page_end = int(page_range["start"]) + len(page_range["suffix"])
    elif not page_range["end"] and not page_range["suffix"]:
        page_end = int(page_range["start"])
    else:
        page_end = int(page_range["end"])
    for i in range(page_start, page_end + 1):
        if contains_page(reference, i):
            return True
        else:
            continue

    return False


def slugify(value):
    """Slugify function extended with `unidecode` for better unicode representation"""
    return _slugify(unidecode(value))
