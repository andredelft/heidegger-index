import yaml
import requests
import click
import regex as re
from pathlib import Path

WORKING_DIR = Path("index")

INDEX_FILE = WORKING_DIR / "heidegger-index.yml"
WORK_REFS_FILE = WORKING_DIR / "works.yml"
OUTPUT_FILE = WORKING_DIR / "works.html"

CITATION_STYLE = "mhra"  # Modern humanities research association
CITEPROC_ENDPOINT = "https://labs.brill.com/citeproc"

yaml.warnings({"YAMLLoadWarning": False})

REF_REGEX = re.compile(r"^(?P<start>\d+)(?:-(?P<end>\d+)|(?P<suffix>f{1,2})\.?)?$")
REF_INTFIELDS = {"start", "end"}


def add_ref(lemma, work, ref, ref_type=None):
    # Open index file
    with open(INDEX_FILE) as f:
        index = yaml.load(f)

    # Verify if reference is given properly
    m = REF_REGEX.search(ref.strip())
    if not m:
        raise click.BadParameter(f'Reference "{ref}" is not recognized')

    # Prepare reference dictionary
    ref_dict = {}
    for k, v in m.groupdict().items():
        if v:
            ref_dict[k] = int(v) if k in REF_INTFIELDS else v

    if ref_type == "r":
        ref_dict["reftype"] = ref_type

    # Determine whether that lemma is already in the index
    try:
        lemma_entry = index[lemma]
        # reftype does not need to be defined here because the lemma reftype is already checked.
    except KeyError:
        # This triggers if the lemma is not present in the index.
        lemma_entry = {work: [ref_dict]}
        if ref_type == "p" or ref_type == "w":
            # Makes sure ref_type 'p' and 'w' are children of 'lemma' instead of 'work'
            lemma_entry["reftype"] = ref_type
    else:
        # This triggers if the lemma is already present in the index.

        if ref_type not in [None, "r"]:
            # Raise error if the reftype given does not match the one already assigned to the lemma.
            try:
                if lemma_entry["reftype"] != ref_type:
                    raise click.BadParameter(
                        f'Cannot assign reftype "{ref_type}" to lemma. Lemma is already defined as being of type "{lemma_entry["reftype"]}".'
                    )
            except KeyError:
                raise click.BadParameter(
                    f"Cannot assign reftype {ref_type} to lemma. Lemma is already defined as having no type."
                )

        try:
            # This triggers if the lemma already contains the work
            lemma_entry[work].append(ref_dict)
        except KeyError:
            # This triggers if the lemma does not contain the work
            lemma_entry[work] = [ref_dict]
            if ref_type == "p" or ref_type == "w":
                # Makes sure ref_type 'p' and 'w' are children of 'lemma' instead of 'work'
                lemma_entry["reftype"] = ref_type

    index[lemma] = lemma_entry

    with open(INDEX_FILE, "w") as f:
        yaml.dump(index, f, allow_unicode=True)


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
