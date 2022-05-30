import click

from .index import *

from heidegger_index.constants import LEMMA_TYPES, REF_TYPES, RELATION_TYPES


@click.command()
@click.argument("lemma", type=str)
@click.argument("work", type=str)
@click.argument("ref", type=str)
@click.option(
    "-l",
    "--lemma-type",
    "lemma_type",
    default=None,
    type=click.Choice(LEMMA_TYPES.keys()),
    help=f"Type of lemma ({', '.join(k + ': ' + v for k, v in LEMMA_TYPES.items())})",
)
@click.option(
    "-r",
    "--ref-type",
    "ref_type",
    default=None,
    type=click.Choice(REF_TYPES.keys()),
    help=f"Type of lemma ({', '.join(k + ': ' + v for k, v in REF_TYPES.items())})",
)
@click.option(
    "-b",
    "--betacode",
    "betacode",
    is_flag=True,
    default=False,
    help="Convert lemma from betacode to unicode",
)
def click_add_ref(lemma, work, ref, lemma_type, ref_type, betacode):
    add_ref(lemma, work, ref, lemma_type, ref_type, betacode)


@click.command()
@click.argument("first_lemma", type=str)
@click.argument("second_lemma", type=str)
@click.argument(
    "rel_type",
    type=click.Choice(RELATION_TYPES.keys()),
)
def click_add_rel(first_lemma, second_lemma, rel_type):
    add_rel(first_lemma, second_lemma, rel_type)


@click.command()
@click.argument("search_term", type=str)
def click_find_ref(search_term):
    find_ref(search_term)


@click.command()
def click_format_refs():
    format_refs()
