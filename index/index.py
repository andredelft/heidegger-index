import yaml
import requests
import click
from pathlib import Path
from betacode.conv import beta_to_uni
from tqdm import tqdm
from itertools import combinations
from pyCTS import CTS_URN

from heidegger_index.utils import match_lemmata, contains_page_range, REF_REGEX
from heidegger_index.constants import LemmaType, MetadataType, RefType, RelationType
from heidegger_index.validators import validate_gnd, validate_iso639_3_lang
from heidegger_index.settings import CITEPROC_ENDPOINT, CITEPROC_STYLE
from django.core.exceptions import ValidationError


WORKING_DIR = Path("index")

INDEX_FILE = WORKING_DIR / "heidegger-index.yml"
WORK_REFS_FILE = WORKING_DIR / "works.yml"
OUTPUT_FILE = WORKING_DIR / "works.html"

REF_INTFIELDS = {"start", "end"}


def add_ref(
    lemma,
    work,
    ref,
    lemma_type=None,
    ref_type=None,
    lang=None,
    betacode=False,
    force=False,
):
    if isinstance(ref, list):
        # Allow ref to be a list, call add_ref for each item and terminate function
        for r in ref:
            add_ref(lemma, work, r, lemma_type, ref_type, lang, betacode)
        return

    try:
        if lemma_type:
            # Validation: lemma_type
            LemmaType(lemma_type)
        if ref_type:
            # Validation: ref_type
            RefType(ref_type)
    except ValueError as e:
        raise click.BadParameter(e)

    # Validation: ref
    m = REF_REGEX.search(str(ref).strip())
    if not m:
        raise click.BadParameter(f"Reference '{ref}' is not recognized")

    if betacode:
        lemma = beta_to_uni(lemma)
        lang = "grc"

    # Open index file
    with open(INDEX_FILE) as f:
        index = yaml.safe_load(f)

    # Prepare reference dictionary
    ref_dict = {}
    if ref == "whole":
        ref_dict["whole"] = True
    else:
        for k, v in m.groupdict().items():
            if v:
                ref_dict[k] = int(v) if k in REF_INTFIELDS else v

    if ref_type:
        ref_dict["type"] = ref_type

    if lang:
        ref_dict["lang"] = lang

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
        if lemma_type:
            # Raise error if the type given does not match the one already assigned to the lemma.
            if "type" not in lemma_entry:
                raise click.BadParameter(
                    f"Cannot assign type '{ref_type}' to lemma. Lemma is already defined as having no type."
                )
            elif lemma_entry["type"] != lemma_type:
                raise click.BadParameter(
                    f"Cannot assign type '{ref_type}' to lemma. Lemma is already defined as being of type '{lemma_entry['type']}'."
                )

        refs = lemma_entry.get("references", {})

        if refs.get(work):
            # Only appends reference if it does not already exist in index.
            r = refs[work]

            if not force:
                # Checks whether exact reference is already in the index.
                if ref_dict in r:
                    raise click.BadParameter(
                        f"Reference already exists for this lemma."
                        f"\nUse option '--force' to ignore this warning and force adding '{ref}' to '{lemma}'."
                        f"\nThis will lead to duplicate references in the index."
                    )
                # UNCOMMENT THIS IF YOU WANT TO PREVENT NEW REFERENCES BEING ADDED IF "WHOLE"
                # IS TRUE.
                # Checks whether the work as a whole is not already a reference for the lemma.
                #
                # elif {"whole": True} in r:
                #     raise click.BadParameter(
                #         f"This work as a whole is already a reference for this lemma."
                #     )

                else:
                    # Check whether pages are allready all in the index
                    for i in r:
                        if contains_page_range(i, ref_dict):
                            if i.get("end"):
                                dash = "-"
                            else:
                                dash = ""
                            raise click.BadParameter(
                                f"Reference '{i.get('start')}{dash}{i.get('end', '')}{i.get('suffix', '')}' already exists for this lemma."
                                f"\nUse option '--force' to ignore this warning and force adding '{ref}' to '{lemma}'."
                                f"\nThis will lead to pages occuring multiple times in seperate references."
                            )

            refs[work].append(ref_dict)

        else:
            refs[work] = [ref_dict]
            if lemma_type:
                lemma_entry["type"] = lemma_type

        lemma_entry["references"] = refs

    # Validation: lang
    if lang:
        validate_iso639_3_lang(lang)
        lemma_entry["lang"] = lang

    index[lemma] = lemma_entry

    with open(INDEX_FILE, "w") as f:
        yaml.safe_dump(index, f, allow_unicode=True)


def add_rel(first_lemma, second_lemma, rel_type):
    # Open index file
    with open(INDEX_FILE) as f:
        index = yaml.safe_load(f)

    # Validation: first_lemma and second_lemma exist
    if first_lemma not in index:
        raise click.BadParameter(f"Lemma '{first_lemma}' not found in index")

    if second_lemma not in index:
        raise click.BadParameter(f"Lemma '{second_lemma}' not found in index")

    try:
        # Validation: rel_type is valid
        RelationType(rel_type)
    except ValueError as e:
        raise click.BadParameter(e)

    first_lemma_dict = index[first_lemma]
    second_lemma_dict = index[second_lemma]

    match rel_type:
        case RelationType.IS_AUTHOR_OF.value:
            if first_lemma_dict.get("type") != LemmaType.PERSON.value:
                raise click.BadParameter(f"Lemma '{first_lemma}' is not a person")
            if second_lemma_dict.get("type") != LemmaType.WORK.value:
                raise click.BadParameter(f"Lemma '{second_lemma}' is not a work")

            index[second_lemma]["author"] = first_lemma
        case RelationType.IS_PARENT_OF.value:
            if any(
                lemma_dict.get("parent") == second_lemma
                for lemma_dict in index.values()
            ):
                raise click.BadParameter(
                    f"Lemma '{second_lemma}' already has children, and therefore cannot itself be a child"
                )
            elif first_lemma_dict.get("parent"):
                raise click.BadParameter(
                    f"Lemma '{first_lemma}' already has a parent, and therefore cannot itself be a parent"
                )

            index[second_lemma]["parent"] = first_lemma
        case RelationType.IS_RELATED_TO.value:
            index[second_lemma]["related"] = second_lemma_dict.get("related", []) + [
                first_lemma
            ]
        case _:
            print("No match")

    with open(INDEX_FILE, "w") as f:
        yaml.safe_dump(index, f, allow_unicode=True)


def find_ref(search_term, max_l_dist=2, num_results=5):
    with open(INDEX_FILE) as f:
        index = yaml.safe_load(f)
    matches = match_lemmata(search_term, index, max_l_dist, True)
    if matches:
        print("\n".join(f"{m[0]}" for m in matches[:num_results]))
    else:
        print("No matches found")


def add_metadata(md_type, lemma, lemma_type, md_value=None, overwrite=False):
    """Add metadata to a lemma of type 'author' or 'work'"""

    # Validation: metadata type is correct
    try:
        MetadataType(md_type)
    except ValueError as e:
        raise click.BadParameter(e)

    # Open index file
    with open(INDEX_FILE) as f:
        index = yaml.safe_load(f)

    # Validation: {md_type: md_value} is not already present in index.
    for l in index:
        # If the lemma already has this value, other logic takes care of it.
        if l == str(lemma):
            continue

        lemma_dict = index[l]
        try:
            lemma_md_dict = lemma_dict["metadata"]
            lemma_md_value = lemma_md_dict[str(md_type)]
        except KeyError:
            continue
        else:
            if lemma_md_value == str(md_value):
                raise click.BadParameter(
                    f"{md_value} is already defined as {md_type} for {l}. {md_type} must be unique."
                )

    # Validation: lemma exists
    try:
        lemma_dict = index[lemma]
    except KeyError:
        raise click.BadParameter(f"Lemma '{lemma}' not found in index.")

    # Validation: lemma type is correct
    if lemma_type:
        try:
            LemmaType(lemma_type)
        except ValueError as e:
            raise click.BadParameter(e)

    # Validation: lemma in index is of same type as lemma_type
    if lemma_type != lemma_dict.get("type"):
        raise click.BadParameter(
            f"Lemma is in the index as '{lemma_dict.get('type')}', not as '{lemma_type}'."
        )

    match md_type:
        case MetadataType.URN:
            # Validation: urn is defined well.
            try:
                cts_urn = CTS_URN(md_value)
            except (TypeError, ValueError):
                raise click.BadParameter(f"'{md_value}' is not a valid CTS URN.")
            if lemma_type == LemmaType.PERSON:
                # Validation: urn is defined well for the type.
                if cts_urn.work:
                    raise click.BadParameter(
                        f"'{cts_urn}' contains a work namespace. Only define up to textgroup for authors."
                    )
            if lemma_type == LemmaType.WORK:
                # Validation: urn is defined well for the type.
                if not cts_urn.work:
                    raise click.BadParameter(
                        f"'{md_value}' does not contain a work namespace. Please provide a valid URN."
                    )

        case MetadataType.GND:
            # Validation: gnd_id is defined well.
            try:
                validate_gnd(str(md_value))
            except ValidationError as e:
                raise click.BadParameter(f"'{md_value}' is not a valid {md_type}: {e}")

            md_value = str(md_value)

        case MetadataType.DIELS_KRANZ:
            try:
                md_value = int(md_value)
            except ValueError:
                raise click.BadParameter(f"'{md_value}' is not a valid {md_type}")

    md_dict = {}
    md_dict[md_type] = md_value

    # Validation: md is not already defined
    try:
        lemma_md_dict = lemma_dict["metadata"]
    except KeyError:
        lemma_dict["metadata"] = md_dict
    else:
        # Validation: md[md_type] is not already defined.
        try:
            lemma_md_value_in_index = lemma_md_dict[str(md_type)]
        except KeyError:
            lemma_md_dict.update({str(md_type): md_value})
        else:
            if lemma_md_value_in_index:
                if overwrite:
                    lemma_md_dict.update({str(md_type): md_value})
                else:
                    if lemma_md_value_in_index == md_value:
                        raise click.BadParameter(
                            f"'{lemma}' has this {md_type} already assigned to it."
                        )
                    else:
                        raise click.BadParameter(
                            f"'{lemma}' already has the following {md_type} defined: '{lemma_md_value_in_index}'."
                        )

        lemma_dict["metadata"] = lemma_md_dict

    index[lemma] = lemma_dict

    # Close and write index file.
    with open(INDEX_FILE, "w") as f:
        yaml.safe_dump(index, f, allow_unicode=True)


# Shorthand functions:


def add_refs(lemmas, *args, **kwargs):
    """Add multiple lemmas with the same reference to the index"""
    for lemma in tqdm(lemmas, desc="Adding references"):
        add_ref(lemma, *args, **kwargs)


def add_interrelated(*lemmas):
    """Add multiple interrelated lemmas to the index"""
    for pair in combinations(lemmas, 2):
        add_rel(*pair, rel_type=RelationType.IS_RELATED_TO)


def format_refs(
    work_refs_file=WORK_REFS_FILE,
    citeproc_endpoint=CITEPROC_ENDPOINT,
    citation_style=CITEPROC_STYLE,
    output_file=OUTPUT_FILE,
):
    with open(work_refs_file) as f:
        refs = yaml.safe_load(f)

    r = requests.post(
        citeproc_endpoint,
        json={"items": refs},
        params={"style": citation_style, "responseformat": "html"},
    )

    with open(output_file, "wb") as f:
        f.write(r.content)
