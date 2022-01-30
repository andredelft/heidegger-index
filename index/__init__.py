import click

from .index import add_ref, format_refs

from heidegger_index.constants import LEMMA_TYPES


@click.command()
@click.argument("lemma", type=str)
@click.argument("work", type=str)
@click.argument("ref", type=str)
@click.option(
    "-t",
    "--type",
    "ref_type",
    default=None,
    type=click.Choice(LEMMA_TYPES.keys()),
    help=f"Type of lemma ({', '.join(k + ': ' + v for k, v in LEMMA_TYPES.items())})",
)
def ar_click(lemma, work, ref, ref_type=None):
    add_ref(lemma, work, ref, ref_type)


@click.command()
def fr_click():
    format_refs()
