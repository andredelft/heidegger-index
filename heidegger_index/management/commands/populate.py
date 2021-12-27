import yaml
from tqdm import tqdm

from django.core.management.base import BaseCommand

from heidegger_index.models import Work, Lemma, PageReference

WORK_REFS_FILE = "works.yml"
INDEX_FILE = "heidegger-index.yml"

yaml.warnings({"YAMLLoadWarning": False})


class Command(BaseCommand):
    def _flush_table(self, Model):
        n, info = Model.objects.all().delete()
        if n:
            self.stdout.write(f"{n} objects deleted")
            for object_type, no_objects in info.items():
                self.stdout.write(f"- {object_type}: {no_objects}")

    def handle(self, *args, **kwargs):
        # Clean DB
        for Model in [PageReference, Lemma, Work]:
            self._flush_table(Model)

        with open(WORK_REFS_FILE) as f:
            works_data = yaml.load(f)

        for work_id, csl_json in tqdm(works_data.items(), desc="Populating works"):
            work_obj = Work(id=work_id, csl_json=csl_json)
            work_obj.save()
            # We need the save method for reference generation, hence no bulk_create

        existing_works = set(works_data.keys())

        with open(INDEX_FILE) as f:
            index_data = yaml.load(f)

        lemma_objs = dict()
        for i, (value, data) in enumerate(index_data.items()):
            lemma_obj = Lemma(id=i, value=value, type=data.pop("reftype", None))
            lemma_obj.create_sort_key()
            lemma_objs[value] = lemma_obj

        Lemma.objects.bulk_create(tqdm(lemma_objs.values(), desc="Populating lemmata"))

        pageref_objs = []
        for lemma_value, works in index_data.items():
            for work, page_ref_list in works.items():

                if work not in existing_works:
                    self.stdout.write(
                        f"Warning: Work {work} does not exist in {WORK_REFS_FILE}, "
                        "will be added with an empty reference"
                    )
                    Work(id=work, csl_json={}).save()
                    existing_works.add(work)

                for ref in page_ref_list:
                    ref.pop("reftype", None)
                    pageref_objs.append(
                        PageReference(
                            work_id=work, lemma=lemma_objs[lemma_value], **ref
                        )
                    )

        PageReference.objects.bulk_create(
            tqdm(pageref_objs, desc="Populating page references")
        )
