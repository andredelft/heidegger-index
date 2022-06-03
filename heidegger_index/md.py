import re
import xml.etree.ElementTree as etree
from markdown import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor

from django.urls import reverse

from heidegger_index.models import Lemma
from heidegger_index.utils import gen_sort_key


def convert_md(content):
    return markdown(
        content, extensions=["smarty", "footnotes", HeideggerIndexExtension()]
    )


RE_LEMMA_LINK = r"\[\[([^\]\n]+?)\]\]"


class LemmaLinkInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        display_value = m.group(1)
        lemma = m.group(1)
        if "|" in lemma:
            display_value, _, lemma = lemma.rpartition("|")

        try:
            lemma_obj = Lemma.objects.get(sort_key=gen_sort_key(lemma))
        except Lemma.DoesNotExist:
            el = etree.Element("span")
            print(f"Link to {lemma} not found (in markdown conversion)")
        else:
            href = reverse("index:lemma-detail", kwargs={"slug": lemma_obj.slug})
            el = etree.Element("a", href=href)

        el.text = display_value.strip()
        return el, m.start(), m.end()


class HeideggerIndexExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            LemmaLinkInlineProcessor(RE_LEMMA_LINK, md), "lemma_link", 40
        )
