import yaml

INDEX_FILE = 'heidegger-index.yml'

yaml.warnings({'YAMLLoadWarning': False})

def add_to_index(lemma, work, page_ref, ref_type=None):
    with open(INDEX_FILE) as f:
        index = yaml.load(f)

    reference = {'pageref': page_ref}
    if ref_type:
        reference['reftype'] = ref_type

    try:
        lemma_entry = index[lemma]
    except KeyError:
        lemma_entry = {work: [reference]}
    else:
        try:
            lemma_entry[work].append(reference)
        except KeyError:
            lemma_entry[work] = [reference]

    index[lemma] = lemma_entry

    with open(INDEX_FILE, 'w') as f:
        yaml.dump(index, f)
