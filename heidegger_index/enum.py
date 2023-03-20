from aenum import Enum


class MemberDoesNotExist(Exception):
    pass


class LabelEnum(str, Enum):
    _init_ = "value label"

    @classmethod
    def display_values(cls) -> str:
        return ", ".join(member.value + ": " + member.label for member in cls)

    @classmethod
    def list_values(cls) -> list[str]:
        return [member.value for member in cls]

    @classmethod
    def list_choices(cls) -> list[tuple[str, str]]:
        """List the enum options in a format compatible with the Django `choices` field,
        e.g. a collection of tuples with the values and human readable labels."""
        return [(member.value, member.label) for member in cls]
