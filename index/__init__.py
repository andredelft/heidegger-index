import click

from .index import *
from heidegger_index.constants import LemmaType, RefType, MetadataType


@click.command()
@click.argument("lemma", type=str)
@click.argument("work", type=str)
@click.argument("ref", type=str)
@click.option(
    "-l",
    "--lemma-type",
    "lemma_type",
    default=None,
    type=click.Choice(LemmaType.list_values()),
    help=f"Lemma type ({LemmaType.display_values()})",
)
@click.option(
    "-r",
    "--ref-type",
    "ref_type",
    default=None,
    type=click.Choice(RefType.list_values()),
    help=f"Reference type ({RefType.display_values()})",
)
@click.option(
    "--language",
    "lang",
    default=None,
    type=str,
    help=f"Lemma language (in ISO 639-3 format)",
)
@click.option(
    "-b",
    "--betacode",
    "betacode",
    is_flag=True,
    default=False,
    help="Convert lemma from betacode to unicode",
)
@click.option(
    "-f",
    "--force",
    "force",
    is_flag=True,
    default=False,
    help="Force reference to be added to lemma",
)
def click_add_ref(lemma, work, ref, lemma_type, ref_type, lang, betacode, force):
    add_ref(lemma, work, ref, lemma_type, ref_type, lang, betacode, force)


@click.command()
@click.argument("first_lemma", type=str)
@click.argument("second_lemma", type=str)
@click.argument(
    "rel_type",
    type=click.Choice(RelationType.list_values()),
)
def click_add_rel(first_lemma, second_lemma, rel_type):
    add_rel(first_lemma, second_lemma, rel_type)


@click.command()
@click.argument(
    "metadata_type",
    type=click.Choice(MetadataType.list_values()),
)
@click.argument("lemma", type=str)
@click.argument(
    "lemma_type",
    type=click.Choice(LemmaType.list_values()),
)
@click.argument("md_value", type=str)
@click.option(
    "-f",
    "--force",
    "overwrite",
    is_flag=True,
    default=False,
    help="Overwrite URN if lemma already has a urn defined.",
)
def click_add_metadata(metadata_type, lemma, lemma_type, md_value, overwrite):
    add_metadata(metadata_type, lemma, lemma_type, md_value, overwrite)


@click.command()
@click.argument("search_term", type=str)
def click_find_ref(search_term):
    find_ref(search_term)


@click.command()
def click_format_refs():
    format_refs()
