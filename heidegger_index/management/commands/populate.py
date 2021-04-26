import yaml
from tqdm import tqdm

from django.core.management.base import BaseCommand

from heidegger_index.models import Work, Lemma, PageReference

REF_FILE = 'references.yml'
INDEX_FILE = 'heidegger-index.yml'

yaml.warnings({'YAMLLoadWarning': False})


class Command(BaseCommand):

    def _flush_table(self, Model):
        n, info = Model.objects.all().delete()
        self.stdout.write(f'{n} objects deleted' + (':' if n else ''))
        for object_type, no_objects in info.items():
            self.stdout.write(f'- {object_type}: {no_objects}')

    def handle(self, *args, **options):
        # Clean DB
        for Model in [PageReference, Lemma, Work]:
            self._flush_table(Model)

        with open(REF_FILE) as f:
            works_data = yaml.load(f)

        Work.objects.bulk_create(
            Work(id=ref_id, reference=ref_data)
            for ref_id, ref_data in tqdm(
                works_data.items(),
                desc="Populating works"
            )
        )

        with open(INDEX_FILE) as f:
            index_data = yaml.load(f)

        lemmas = {
            # Create all lemma objects, and index them by term
            term: Lemma(id=i, term=term, type=data.pop('reftype', None))
            for i, (term, data) in enumerate(index_data.items())
        }
        Lemma.objects.bulk_create(tqdm(lemmas.values(), desc="Populating lemmata"))

        # TODO: Populate page refs
