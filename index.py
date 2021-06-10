import yaml
import click
import regex as re

from heidegger_index.constants import LEMMA_TYPES

INDEX_FILE = 'heidegger-index.yml'

yaml.warnings({'YAMLLoadWarning': False})

REF_REGEX = re.compile(r'^(?P<start>\d+)(?:-(?P<end>\d+)|(?P<suffix>f{1,2})\.?)?$')
REF_INTFIELDS = {'start', 'end'}


@click.command()
@click.argument('lemma', type=str)
@click.argument('work', type=str)
@click.argument('ref', type=str)
@click.option(
    '-t', '--type', 'ref_type', default=None,
    type=click.Choice(LEMMA_TYPES.keys()),
    help=f"Type of lemma ({', '.join(k + ': ' + v for k, v in LEMMA_TYPES.items())})"
)
def add_to_index(lemma, work, ref, ref_type=None):
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
    if ref_type != 'p' and ref_type is not None:
        ref_dict['reftype'] = ref_type

    try:
        lemma_entry = index[lemma]
    except KeyError:
        # Makes sure ref_type 'p' is a child of 'lemma' instead of 'work'
        if ref_type == 'p':
            lemma_entry = {work: [ref_dict]}
            lemma_entry['reftype'] = ref_type
        else:
            lemma_entry = {work: [ref_dict]}
    else:
        try:
            lemma_entry[work].append(ref_dict)
        except KeyError:
            lemma_entry[work] = [ref_dict]

    index[lemma] = lemma_entry

    with open(INDEX_FILE, 'w') as f:
        yaml.dump(index, f, allow_unicode=True)
