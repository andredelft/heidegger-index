import xml.etree.ElementTree as etree
from markdown import markdown, util, Extension
from markdown.blockprocessors import BlockQuoteProcessor
from markdown.inlinepatterns import InlineProcessor

from django.urls import reverse
from django.conf import settings

from heidegger_index.models import Lemma, Work
from heidegger_index.utils import gen_sort_key


def convert_md(content):
    return markdown(
        content, extensions=["smarty", "footnotes", HeideggerIndexExtension()]
    )


RE_LEMMA_LINK = r"\[\[([^\]\n]+)\]\]"  # e.g. [[Aristoteles]]
RE_WORK_CIT = r"\[@([^\]\n]+?)\]"  # e.g. [@GA-62, p. 4]


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
            print(f"Markdown conversion: link to {lemma} not found")
        else:
            href = reverse("index:lemma-detail", kwargs={"slug": lemma_obj.slug})
            el = etree.Element("a", href=href)

        el.text = display_value.strip()
        return el, m.start(), m.end()


class WorkCitationInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        citation = m.group(1)
        if "," in citation:
            work_key, citation = citation.split(",", maxsplit=1)
        else:
            work_key = citation
            citation = ""

        work_key = work_key.strip()
        citation = citation.strip()

        el = etree.Element("span")
        el.text = "("  # Opening citation
        try:
            work_obj = Work.objects.get(key=work_key)
        except Work.DoesNotExist:
            work_el = etree.SubElement(el, "span")
            work_el.attrib["class"] = "italic"
            print(f"Markdown conversion: cited work {work_key} does not exist")
        else:
            href = reverse("index:work-detail", kwargs={"slug": work_obj.slug})
            work_el = etree.SubElement(el, "a", href=href)
            work_el.attrib["class"] = settings.TAILWIND_CLASSES["link_decoration"]

        work_el.text = work_key

        if citation:
            work_el.tail = f", {citation.strip()})"  # Closing citation
        else:
            work_el.tail = ")"

        return el, m.start(), m.end()


class NonLazyBlockQuoteBlockProcessor(BlockQuoteProcessor):
    """A copy of the BlockQuoteProcessor without ['lazy blockquotes'](https://daringfireball.net/projects/markdown/syntax#blockquote). Taken from: https://github.com/atodorov/Markdown-No-Lazy-BlockQuote-Extension"""

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = self.RE.search(block)
        if m:
            before = block[: m.start()]  # Lines before blockquote
            # Pass lines before blockquote in recursively for parsing forst.
            self.parser.parseBlocks(parent, [before])
            # Remove ``> `` from begining of each line.
            block = "\n".join(
                [self.clean(line) for line in block[m.start() :].split("\n")]
            )

        # no lazy blockquotes
        quote = util.etree.SubElement(parent, "blockquote")

        # Recursively parse block with blockquote as parent.
        # change parser state so blockquotes embedded in lists use p tags
        self.parser.state.set("blockquote")
        self.parser.parseChunk(quote, block)
        self.parser.state.reset()


class HeideggerIndexExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(
            LemmaLinkInlineProcessor(RE_LEMMA_LINK, md), "lemma_link", 40
        )
        md.inlinePatterns.register(
            WorkCitationInlineProcessor(RE_WORK_CIT, md), "work_cit", 41
        )
        md.parser.blockprocessors["quote"] = NonLazyBlockQuoteBlockProcessor(md.parser)
