from .enum import LabelEnum


class LemmaType(LabelEnum):
    PERSON = "p", "person"
    WORK = "w", "work"
    GEOGRAPHICAL = "g", "geographical"


class MetadataType(LabelEnum):
    URN = "urn", "Uniform Resource Name"
    GND = "gnd", "Gemeinsame Normdatei"
    DIELS_KRANZ = "dk", "Diels-Kranz ID"


class RefType(LabelEnum):
    RELATED = "r", "related"


class RelationType(LabelEnum):
    IS_PARENT_OF = "p", "is parent of"
    IS_AUTHOR_OF = "a", "is author of"
    IS_RELATED_TO = "r", "is related to"
