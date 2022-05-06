from requests import HTTPError
import yaml
from tqdm import tqdm
from glob import glob
from pathlib import Path
from markdown import markdown

from django.core.management.base import BaseCommand
from django.conf import settings

from heidegger_index.models import Work, Lemma, PageReference

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

        with open(settings.WORK_REFS_FILE) as f:
            works_data = yaml.load(f)

        descriptions = {}
        for fpath in tqdm(
            glob(str(settings.DESCRIPTIONS_DIR / "*.md")), desc="Loading descriptions"
        ):
            lemma = Path(fpath).stem
            with open(fpath) as f:
                content = markdown(f.read(), extensions=["smarty", "footnotes"])
            descriptions[lemma] = content

        work_objs = []
        for work_id, csl_json in tqdm(
            works_data.items(), desc="Generating work references"
        ):
            work_obj = Work(id=work_id, csl_json=csl_json)
            try:
                work_obj.gen_reference()
            except HTTPError as e:
                self.stdout.write(f"Skipping {work_id} because of HTTP error: {e}")
            else:
                work_objs.append(work_obj)

        Work.objects.bulk_create(tqdm(work_objs, desc="Populating works"))

        existing_works = set(works_data.keys())

        with open(settings.INDEX_FILE) as f:
            index_data = yaml.load(f)

        lemma_objs = dict()
        sort_keys = dict()
        for i, (value, data) in enumerate(index_data.items()):
            lemma_obj = Lemma(id=i, value=value, type=data.pop("reftype", None))
            description = descriptions.get(value)
            if description:
                lemma_obj.description = description
            lemma_obj.create_sort_key()
            if lemma_obj.sort_key in sort_keys.keys():
                self.stdout.write(
                    f'Lemma "{value}" shares sort key "{lemma_obj.sort_key}" with "{sort_keys[lemma_obj.sort_key]}". The first lemma will be omitted.'
                )
            else:
                sort_keys[lemma_obj.sort_key] = value
                lemma_objs[value] = lemma_obj

        Lemma.objects.bulk_create(tqdm(lemma_objs.values(), desc="Populating lemmata"))

        pageref_objs = []
        # Filter all omitted lemmas that share a sort key
        index_data = {k: v for k, v in index_data.items() if k in lemma_objs.keys()}
        for lemma_value, works in index_data.items():
            for work, page_ref_list in works.items():

                if work not in existing_works:
                    self.stdout.write(
                        f"Warning: Work {work} does not exist in {settings.WORK_REFS_FILE.name}, "
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
