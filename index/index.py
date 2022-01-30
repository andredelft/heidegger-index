import yaml
import requests
import click
import regex as re
from pathlib import Path

CURRENT_DIR = Path(__file__).parent

INDEX_FILE = CURRENT_DIR / "heidegger-index.yml"
WORK_REFS_FILE = CURRENT_DIR / "works.yml"
OUTPUT_FILE = CURRENT_DIR / "works.html"

CITATION_STYLE = "mhra"  # Modern humanities research association
CITEPROC_ENDPOINT = "https://labs.brill.com/citeproc"

yaml.warnings({"YAMLLoadWarning": False})

REF_REGEX = re.compile(r"^(?P<start>\d+)(?:-(?P<end>\d+)|(?P<suffix>f{1,2})\.?)?$")
REF_INTFIELDS = {"start", "end"}


def add_ref(lemma, work, ref, ref_type=None):
    with open(INDEX_FILE) as f:
        index = yaml.load(f)

    m = REF_REGEX.search(ref.strip())
    if not m:
        raise click.BadParameter(f'Reference "{ref}" is not recognized')

    ref_dict = {}
    for k, v in m.groupdict().items():
        if v:
            ref_dict[k] = int(v) if k in REF_INTFIELDS else v

    # Makes sure ref_type 'p' is a child of 'lemma' instead of 'work'
    if ref_type != "p" and ref_type is not None:
        ref_dict["reftype"] = ref_type

    try:
        lemma_entry = index[lemma]
    except KeyError:
        # Makes sure ref_type 'p' is a child of 'lemma' instead of 'work'
        if ref_type == "p":
            lemma_entry = {work: [ref_dict]}
            lemma_entry["reftype"] = ref_type
        else:
            lemma_entry = {work: [ref_dict]}
    else:
        try:
            lemma_entry[work].append(ref_dict)
        except KeyError:
            lemma_entry[work] = [ref_dict]

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
