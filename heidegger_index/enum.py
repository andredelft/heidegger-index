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
    def list_choices(cls) -> tuple[str, str]:
        return [(member.value, member.label) for member in cls]
