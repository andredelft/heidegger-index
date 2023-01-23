from typing import List
from requests import HTTPError
import yaml
from tqdm import tqdm
from glob import glob
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from heidegger_index.models import Work, Lemma, PageReference
from heidegger_index.utils import gen_sort_key
from heidegger_index.md import convert_md
from heidegger_index.constants import GND, URN

yaml.warnings({"YAMLLoadWarning": False})


class Command(BaseCommand):
    def _flush_table(self, Model):
        n, info = Model.objects.all().delete()
        if n:
            self.stdout.write(f"{n} objects deleted")
            for object_type, no_objects in info.items():
                self.stdout.write(f"- {object_type}: {no_objects}")

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-external-calls",
            "-n",
            action="store_true",
            help="Run without external calls to speed up the populate script (but skip some fields).",
        )

        return super().add_arguments(parser)

    def handle(self, *args, **kwargs):
        perform_external_calls = not kwargs.get("no_external_calls")

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
                md_content = f.read()
            description_by_sort_key[gen_sort_key(lemma)] = md_content

        # Load index data
        with open(settings.INDEX_FILE) as f:
            index_data = yaml.load(f)

        # Populate works and index by title and by key
        work_objs = []
        work_by_title = {}
        work_by_key = {}

        for i, (work_key, csl_json) in enumerate(
            tqdm(works_data.items(), desc="Generating work references")
        ):
            work_obj = Work(id=i, key=work_key, csl_json=csl_json)

            if perform_external_calls:
                try:
                    work_obj.gen_reference()
                except HTTPError as e:
                    self.stdout.write(
                        f"Skipping {work_key} reference generation because of HTTP error: {e}"
                    )
            else:
                work_obj.reference = "—"

            work_objs.append(work_obj)

            title = work_obj.csl_json.get("title")
            if title:
                work_by_title[title] = work_obj
            short_title = work_obj.csl_json.get("title-short")
            if short_title:
                work_by_title[short_title] = work_obj

            work_by_key[work_key] = work_obj

        Work.objects.bulk_create(tqdm(work_objs, desc="Populating works"))

        # Setting work hierarchy
        works_with_parents = []
        for i, work in enumerate(work_objs):
            container_title = work.csl_json.get("container-title")
            if container_title:
                parent = work_by_title.get(container_title)
                if parent:
                    work.parent = parent
                    works_with_parents.append(work)

        Work.objects.bulk_update(
            tqdm(works_with_parents, desc="Setting work hierarchy"), ["parent"]
        )

        # Populate lemmas
        lemma_objs = dict()
        sort_keys = dict()
        for i, (value, data) in enumerate(
            tqdm(index_data.items(), desc="Preparing lemmata for populate")
        ):
            md = data.get("metadata", {})
            lemma_obj = Lemma(
                id=i,
                value=value,
                type=data.get("type", None),
                urn=md.get(URN, None),
                gnd=md.get(GND, None)
            )
            if perform_external_calls:
                try:
                    lemma_obj.load_work_text()
                except HTTPError as e:
                    self.stdout.write(
                        f"Skipping {lemma_obj} because of HTTP error: {e}"
                    )
            lemma_obj.create_sort_key()
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
        # and populate descriptions and full work texts
        for lemma_value, lemma_data in index_data.items():
            lemma_obj = lemma_objs[lemma_value]

            # Parents
            parent_value = lemma_data.get("parent")
            if parent_value:
                lemma_obj.parent = lemma_objs[parent_value]

            # Authors
            author_value = lemma_data.get("author")
            if author_value:
                author = lemma_objs.get(author_value)
                if author:
                    lemma_obj.author = author

            # Related
            for related_lemma_value in lemma_data.get("related", []):
                lemma_obj.related.add(lemma_objs[related_lemma_value])

            lemma_obj.work = work_title_map.get(lemma_value)

            lemma_objs[lemma_value] = lemma_obj

            # Descriptions
            description = description_by_sort_key.get(lemma_obj.sort_key)
            if description:
                lemma_obj.description = convert_md(description)

        # ManyToMany field 'related' is updated automatically, ForeignKeys are not
        Lemma.objects.bulk_update(
            tqdm(
                lemma_objs.values(),
                desc="Setting foreign key relations and descriptions",
            ),
            ["parent", "author", "work", "description"],
        )

        # Populate page references
        pageref_objs = []
        for lemma_value, lemma_data in index_data.items():
            for work_key, ref_list in lemma_data.get("references", {}).items():

                if work_key not in work_by_key.keys():
                    self.stdout.write(
                        f"Warning: Work {work_key} does not exist in {settings.WORK_REFS_FILE.name}, will be added with an empty reference"
                    )
                    work_obj = Work(key=work_key, csl_json={})
                    work_obj.save()
                    work_by_key[work_key] = work_obj

                for ref in ref_list:
                    pageref_objs.append(
                        PageReference(
                            work=work_by_key[work_key],
                            lemma=lemma_objs[lemma_value],
                            **ref,
                        )
                    )

        PageReference.objects.bulk_create(
            tqdm(pageref_objs, desc="Populating page references")
        )
