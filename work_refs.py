import requests
import yaml

CITATION_STYLE = 'mhra' # Modern humanities research association
WORK_REFS_FILE = 'works.yml'
CITEPROC_ENDPOINT = 'https://labs.brill.com/citeproc'
OUTPUT_FILE = 'works.html'

yaml.warnings({'YAMLLoadWarning': False})

def format_refs(work_refs_file=WORK_REFS_FILE, citeproc_endpoint=CITEPROC_ENDPOINT, citation_style=CITATION_STYLE, output_file=OUTPUT_FILE):
    with open(work_refs_file) as f:
        refs = yaml.load(f)

    r = requests.post(CITEPROC_ENDPOINT, json={'items': refs}, params={'style': citation_style, 'responseformat': 'html'})

    with open(output_file, 'wb') as f:
        f.write(r.content)

if __name__ == '__main__':
    format_refs()
