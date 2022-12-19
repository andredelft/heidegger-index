from django.core.exceptions import ValidationError

import re

## https://wiki.dnb.de/pages/viewpage.action?pageId=48139522

def validate_gnd(value):
    # Validate type
    if type(value) == str or type(value) == int:
        # Validate with regex according to https://www.wikidata.org/wiki/Property:P227
        GND_REGEX = r"1[012]?\d{7}[0-9X]|[47]\d{6}-\d|[1-9]\d{0,7}-[0-9X]|3\d{7}[0-9X]"
        regex = re.compile(GND_REGEX, re.IGNORECASE)
        if not regex.match(value):
            raise ValidationError(
                f"{value} is not syntactically valid."
                )

        sum = 0
        for i, d in enumerate(reversed(value)):
            if i == 0:
                control_digit = d
                continue
            sum = sum + (int(d) * (i + 1))

        print(f"control digit: {control_digit}")
        print(f"{sum}")

        cd_calculated = ((11 - (sum % 11)) % 11)
        if cd_calculated == 10:
            cd_calculated = 'X'

        print(cd_calculated)
        
        if str(cd_calculated) != str(control_digit):
            raise ValidationError(
                f"{value}'s control digit is not valid."
            )

    else:
        raise ValidationError(
            f"{value} is not a valid string or integer."
        )