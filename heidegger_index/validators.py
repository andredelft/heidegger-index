from django.core.exceptions import ValidationError
from .constants import MetadataType

import re

GND_REGEX = r"1[012]?\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]"
DK_REGEX = r"^\d{1,2}$"  # https://www.wikidata.org/wiki/Property:P8163
ZENO_REGEX = r"^\d{11}$"  # https://www.wikidata.org/wiki/Property:P11802


def validate_simple_regex(value: str | int, pattern: str, name: str = "identifier"):
    if not re.match(pattern, str(value)):
        raise ValidationError(f"{value} is not a valid {name}")


## https://wiki.dnb.de/pages/viewpage.action?pageId=48139522
# Should match https://de.wikipedia.org/wiki/Gemeinsame_Normdatei#Entitätsidentifikator
# and https://de.wikipedia.org/wiki/Personennamendatei#Aufbau


def validate_gnd(value):
    # ONLY WORKS FOR PND / POST-2012 entries.

    # Validate type
    if type(value) == str or type(value) == int:
        value = str(value)
        # Validate with regex according to https://www.wikidata.org/wiki/Property:P227
        regex = re.compile(GND_REGEX, re.IGNORECASE)
        if not regex.match(value):
            raise ValidationError(f"{value} is not syntactically valid.")

        if type(value) == str:
            value = re.sub(r"[^0-9X]", "", value)

        sum = 0
        for i, d in enumerate(reversed(value)):
            if i == 0:
                control_digit = d
                continue
            sum = sum + (int(d) * (i + 1))

        cd_calculated = (11 - (sum % 11)) % 11
        if cd_calculated == 10:
            cd_calculated = "X"

        if str(cd_calculated) != str(control_digit):
            raise ValidationError(f"{value}'s control digit is not valid.")

    else:
        raise ValidationError(f"{value} is not a valid string or integer.")


def validate_dk(value: int | str):
    validate_simple_regex(value, DK_REGEX, MetadataType.DIELS_KRANZ.label)


def validate_zeno(value: str | int):
    validate_simple_regex(value, ZENO_REGEX, MetadataType.ZENO.label)
