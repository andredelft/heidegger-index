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
        if n:
            self.stdout.write(f'{n} objects deleted')
            for object_type, no_objects in info.items():
                self.stdout.write(f'- {object_type}: {no_objects}')

    def handle(self, *args, **options):
        # Clean DB
        for Model in [PageReference, Lemma, Work]:
            self._flush_table(Model)

        with open(REF_FILE) as f:
            works_data = yaml.load(f)

        Work.objects.bulk_create(
            Work(id=work_id, csl_json=csl_json)
            for work_id, csl_json in tqdm(
                works_data.items(),
                desc="Populating works"
            )
        )

        existing_works = set(works_data.keys())

        with open(INDEX_FILE) as f:
            index_data = yaml.load(f)

        lemma_objs = {
            # Create all lemma objects, and index them by value
            value: Lemma(id=i, value=value, type=data.pop('reftype', None))
            for i, (value, data) in enumerate(index_data.items())
        }
        Lemma.objects.bulk_create(
            tqdm(lemma_objs.values(), desc="Populating lemmata")
        )

        pageref_objs = []
        for lemma_value, works in index_data.items():
            for work, page_ref_list in works.items():

                if work not in existing_works:
                    self.stdout.write(
                        f'Warning: Work {work} does not exist in {REF_FILE}, '
                        'will be added with an empty reference'
                    )
                    Work(
                        id=work, csl_json={}
                    ).save()
                    existing_works.add(work)

                pageref_objs += [
                    PageReference(
                        work_id=work, lemma=lemma_objs[lemma_value],
                        value=ref['pageref']
                    ) for ref in page_ref_list
                ]

        PageReference.objects.bulk_create(
            tqdm(pageref_objs, desc="Populating page references")
        )
