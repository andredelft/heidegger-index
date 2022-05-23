from requests import HTTPError
import yaml
from tqdm import tqdm
from glob import glob
from pathlib import Path
from markdown import markdown

from django.core.management.base import BaseCommand
from django.conf import settings

from heidegger_index.models import Work, Lemma, PageReference
from heidegger_index.utils import gen_sort_key

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

        # Load work data
        with open(settings.WORK_REFS_FILE) as f:
            works_data = yaml.load(f)

        # Load descriptions
        description_by_sort_key = {}
        for fpath in tqdm(
            glob(str(settings.DESCRIPTIONS_DIR / "*.md")), desc="Loading descriptions"
        ):
            lemma = Path(fpath).stem
            with open(fpath) as f:
                content = markdown(f.read(), extensions=["smarty", "footnotes"])
            description_by_sort_key[gen_sort_key(lemma)] = content

        # Load index data
        with open(settings.INDEX_FILE) as f:
            index_data = yaml.load(f)

        # Populate works
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

        # Populate lemmas
        lemma_objs = dict()
        sort_keys = dict()
        for i, (value, data) in enumerate(index_data.items()):
            lemma_obj = Lemma(id=i, value=value, type=data.get("type", None))
            lemma_obj.create_sort_key()
            description = description_by_sort_key.get(lemma_obj.sort_key)
            if description:
                lemma_obj.description = description
            if lemma_obj.sort_key in sort_keys.keys():
                self.stdout.write(
                    f'Lemma "{value}" shares sort key "{lemma_obj.sort_key}" with "{sort_keys[lemma_obj.sort_key]}". The first lemma will be omitted.'
                )
            else:
                sort_keys[lemma_obj.sort_key] = value
                lemma_objs[value] = lemma_obj

        # Filter all omitted lemmas in index_data that share a sort key
        index_data = {k: v for k, v in index_data.items() if k in lemma_objs.keys()}

        Lemma.objects.bulk_create(tqdm(lemma_objs.values(), desc="Populating lemmata"))

        work_title_map = {
            work.csl_json.get("title") or work.csl_json.get("title-short"): work
            for work in work_objs
        }

        # Loop a second time through lemma_data to set parent, author and related fields
        for lemma_value, lemma_data in index_data.items():
            lemma_obj = lemma_objs[lemma_value]
            parent_value = lemma_data.get("parent")
            if parent_value:
                lemma_obj.parent = lemma_objs[parent_value]

            author_value = lemma_data.get("author")
            if author_value:
                author = lemma_objs.get(author_value)
                if author:
                    lemma_obj.author = author

            for related_lemma_value in lemma_data.get("related", []):
                lemma_obj.related.add(lemma_objs[related_lemma_value])

            lemma_obj.work = work_title_map.get(lemma_value)

            lemma_objs[lemma_value] = lemma_obj

        # ManyToMany field 'related' is updated automatically, ForeignKeys are not
        Lemma.objects.bulk_update(
            tqdm(lemma_objs.values(), desc="Setting foreign key relations"),
            ["parent", "author", "work"],
        )

        # Populate page references
        pageref_objs = []
        for lemma_value, lemma_data in index_data.items():
            for work, ref_list in lemma_data.get("references", {}).items():

                if work not in existing_works:
                    self.stdout.write(
                        f"Warning: Work {work} does not exist in {settings.WORK_REFS_FILE.name}, will be added with an empty reference"
                    )
                    Work(id=work, csl_json={}).save()
                    existing_works.add(work)

                for ref in ref_list:
                    pageref_objs.append(
                        PageReference(
                            work_id=work, lemma=lemma_objs[lemma_value], **ref
                        )
                    )

        PageReference.objects.bulk_create(
            tqdm(pageref_objs, desc="Populating page references")
        )
