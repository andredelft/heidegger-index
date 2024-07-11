from unidecode import unidecode
import re
from fuzzysearch import find_near_matches

from django.template.defaultfilters import slugify as _slugify

PREFIXES = ["der", "die", "das", "den"]

PREFIX_FILTER = re.compile(rf'^(?:{"|".join(PREFIXES)})\s+')

REF_REGEX = re.compile(
    r"^(?:whole|(?P<start>\d+)(?:-(?P<end>\d+)|(?P<suffix>f{1,2})\.?)?)$"
)

# This is the NUMBER FORM unicode block
NUMERIC_UNICODE_VALUES = {
    188: 0.25,
    189: 0.5,
    190: 0.75,
    8528: 0.142857,
    8529: 0.111,
    8530: 0.1,
    8531: 0.333,
    8532: 0.666,
    8533: 0.2,
    8534: 0.4,
    8535: 0.6,
    8536: 0.8,
    8537: 0.166,
    8538: 0.833,
    8539: 0.125,
    8540: 0.375,
    8541: 0.625,
    8542: 0.875,
    8543: 1,
    8544: 1,
    8545: 2,
    8546: 3,
    8547: 4,
    8548: 5,
    8549: 6,
    8550: 7,
    8551: 8,
    8552: 9,
    8553: 10,
    8554: 11,
    8555: 12,
    8556: 50,
    8557: 100,
    8558: 500,
    8559: 1000,
    8560: 1,
    8561: 2,
    8562: 3,
    8563: 4,
    8564: 5,
    8565: 6,
    8566: 7,
    8567: 8,
    8568: 9,
    8569: 10,
    8570: 11,
    8571: 12,
    8572: 50,
    8573: 100,
    8574: 500,
    8575: 1000,
    8576: 1000,
    8577: 5000,
    8578: 10000,
    8579: 100,
    8580: 100,
    8581: 6,
    8582: 50,
    8583: 50000,
    8584: 100000,
    8585: 0,
    8586: 10,
    8587: 11,
}


def convert_numeric_unicode(value: str) -> str:
    new_value = ""
    for char in value:
        new_value += str(NUMERIC_UNICODE_VALUES.get(ord(char), char))
    return new_value


def gen_work_sort_key(key: str) -> str:
    # Strip and add a leading zero to single digits (GA 5 -> GA 05)
    return re.sub("\d+", lambda m: f"{m.group():0>2}", key.strip())


def gen_lemma_sort_key(key: str) -> str:
    # Strip surrounding whitespaces
    sort_key = key.strip()
    # Convert numeric unicode to value
    sort_key = convert_numeric_unicode(sort_key)
    # Normalize unicode
    sort_key = unidecode(sort_key)
    # Convert to lowercase
    sort_key = sort_key.lower()
    # Filter some prefixes
    sort_key, n = PREFIX_FILTER.subn("", sort_key)
    while n:
        sort_key, n = PREFIX_FILTER.subn("", sort_key)
    # Add leading zero's to numbers to improve number sorting
    sort_key = re.sub("\d+", lambda m: f"{m.group():0>5}", sort_key)
    return sort_key


def match_lemmata(search_term, index, max_l_dist=2, include_search_term=True):

    key_to_lemma = {gen_lemma_sort_key(lemma): lemma for lemma in index.keys()}
    keys = key_to_lemma.keys()

    if not include_search_term:
        # Remove subject lemma from list
        keys = [k for k in keys if k != gen_lemma_sort_key(search_term)]

    matches = [
        (
            key_to_lemma[key],
            find_near_matches(
                gen_lemma_sort_key(search_term),
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

    if reference.get("end"):
        if page >= reference.get("start") and page <= reference.get("end"):
            return True
    if not reference.get("end") and reference.get("start"):
        if page == reference.get("start"):
            return True
        elif reference.get("suffix") == "f" and page == reference.get("start") + 1:
            return True
        elif reference.get("suffix") == "ff" and page == reference.get("start") + 2:
            return True

    return False


def contains_page_range(reference: dict, page_range) -> bool:
    if not type(page_range) == dict:
        page_range = re.fullmatch(REF_REGEX, page_range).groupdict()

        if not page_range:
            raise ValueError("Not a valid page range given.")

    page_start = int(page_range.get("start"))

    if not page_range.get("end") and page_range.get("suffix"):
        page_end = int(page_range["start"]) + len(page_range.get("suffix"))
    elif not page_range.get("end") and not page_range.get("suffix"):
        page_end = int(page_range["start"])
    else:
        page_end = int(page_range.get("end"))
    for i in range(page_start, page_end + 1):
        if contains_page(reference, i):
            return True
        else:
            continue

    return False


def slugify(value):
    """Slugify function extended with `unidecode` for better unicode representation"""
    return _slugify(unidecode(value))
