import yaml
import requests
import click
import regex as re
from pathlib import Path
from betacode.conv import beta_to_uni

from heidegger_index.utils import match_lemmata
from heidegger_index.constants import (
    LEMMA_TYPES,
    PERSON,
    WORK,
    REF_TYPES,
    RELATION_TYPES,
    IS_PARENT_OF,
    IS_AUTHOR_OF,
    IS_RELATED_TO,
)


WORKING_DIR = Path("index")

INDEX_FILE = WORKING_DIR / "heidegger-index.yml"
WORK_REFS_FILE = WORKING_DIR / "works.yml"
OUTPUT_FILE = WORKING_DIR / "works.html"

CITATION_STYLE = "mhra"  # Modern humanities research association
CITEPROC_ENDPOINT = "https://labs.brill.com/citeproc"

yaml.warnings({"YAMLLoadWarning": False})

REF_REGEX = re.compile(r"^(?P<start>\d+)(?:-(?P<end>\d+)|(?P<suffix>f{1,2})\.?)?$")
REF_INTFIELDS = {"start", "end"}


def add_ref(lemma, work, ref, lemma_type=None, ref_type=None, betacode=False):

    # Validation: lemma_type
    if lemma_type and lemma_type not in LEMMA_TYPES:
        raise click.BadParameter(
            f"Lemma type must be one of: {', '.join(LEMMA_TYPES.values())}"
        )

    # Validation: ref_type
    if ref_type and ref_type not in REF_TYPES:
        raise click.BadParameter(
            f"Reference type must be one of: {', '.join(REF_TYPES.values())}"
        )

    # Validation: ref
    m = REF_REGEX.search(str(ref).strip())
    if not m:
        raise click.BadParameter(f"Reference '{ref}' is not recognized")

    if betacode:
        lemma = beta_to_uni(lemma)

    # Open index file
    with open(INDEX_FILE) as f:
        index = yaml.load(f)

    # Prepare reference dictionary
    ref_dict = {}
    for k, v in m.groupdict().items():
        if v:
            ref_dict[k] = int(v) if k in REF_INTFIELDS else v

    if ref_type:
        ref_dict["type"] = ref_type

    # Determine whether that lemma is already in the index
    try:
        lemma_entry = index[lemma]
    except KeyError:
        # This triggers if the lemma is not present in the index.
        lemma_entry = {"references": {work: [ref_dict]}}
        if lemma_type:
            lemma_entry["type"] = lemma_type
    else:
        # This triggers if the lemma is already present in the index.
        if lemma_type in LEMMA_TYPES:
            # Raise error if the type given does not match the one already assigned to the lemma.
            if "type" not in lemma_entry:
                raise click.BadParameter(
                    f"Cannot assign type '{ref_type}' to lemma. Lemma is already defined as having no type."
                )
            elif lemma_entry["type"] != lemma_type:
                raise click.BadParameter(
                    f"Cannot assign type '{ref_type}' to lemma. Lemma is already defined as being of type '{lemma_entry['type']}'."
                )

        if lemma_entry.get(work):
            lemma_entry["references"][work].append(ref_dict)
        else:
            lemma_entry["references"][work] = [ref_dict]
            if lemma_type:
                lemma_entry["type"] = lemma_type

    index[lemma] = lemma_entry

    with open(INDEX_FILE, "w") as f:
        yaml.dump(index, f, allow_unicode=True)


def add_rel(first_lemma, second_lemma, rel_type):

    # Open index file
    with open(INDEX_FILE) as f:
        index = yaml.load(f)

    # Validation: first_lemma and second_lemma exist
    if first_lemma not in index:
        raise click.BadParameter(f"Lemma '{first_lemma}' not found in index")

    if second_lemma not in index:
        raise click.BadParameter(f"Lemma '{second_lemma}' not found in index")

    # Validation: rel_type is valid
    if rel_type not in RELATION_TYPES:
        raise click.BadParameter(
            f"Relation type must be one of: {', '.join(RELATION_TYPES.values())}"
        )

    first_lemma_dict = index[first_lemma]
    second_lemma_dict = index[second_lemma]

    if rel_type == IS_AUTHOR_OF:
        if first_lemma_dict.get("type") != PERSON:
            raise click.BadParameter(f"Lemma '{first_lemma}' is not a person")
        if second_lemma_dict.get("type") != WORK:
            raise click.BadParameter(f"Lemma '{second_lemma}' is not a work")

        index[second_lemma]["author"] = first_lemma
    elif rel_type == IS_PARENT_OF:
        if second_lemma_dict.get("children"):
            raise click.BadParameter(
                f"Lemma '{first_lemma}' already has children, and therefore cannot itself be a child"
            )
        elif any(lem_dict.get("parent") == first_lemma for lem_dict in index.values()):
            raise click.BadParameter(
                f"Lemma '{first_lemma}' already has a parent, and therefore cannot itself be a parent"
            )

        index[second_lemma]["parent"] = first_lemma
    elif rel_type == IS_RELATED_TO:
        index[second_lemma]["related"] = second_lemma_dict.get("related", []) + [
            first_lemma
        ]

    with open(INDEX_FILE, "w") as f:
        yaml.dump(index, f, allow_unicode=True)


def find_ref(search_term, max_l_dist=2, num_results=5):
    with open(INDEX_FILE) as f:
        index = yaml.load(f)
    matches = match_lemmata(search_term, index, max_l_dist, True)
    if matches:
        print("\n".join(f"{m[0]}" for m in matches[:num_results]))
    else:
        print("No matches found")


def format_refs(
    work_refs_file=WORK_REFS_FILE,
    citeproc_endpoint=CITEPROC_ENDPOINT,
    citation_style=CITATION_STYLE,
    output_file=OUTPUT_FILE,
):
    with open(work_refs_file) as f:
        refs = yaml.load(f)

    r = requests.post(
        citeproc_endpoint,
        json={"items": refs},
        params={"style": citation_style, "responseformat": "html"},
    )

    with open(output_file, "wb") as f:
        f.write(r.content)
