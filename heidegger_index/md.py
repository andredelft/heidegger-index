import xml.etree.ElementTree as etree
from markdown import markdown, util, Extension
from markdown.blockprocessors import BlockQuoteProcessor
from markdown.inlinepatterns import InlineProcessor

from django.urls import reverse
from django.conf import settings

from heidegger_index.models import Lemma, Work
from heidegger_index.utils import gen_lemma_sort_key


def convert_md(content):
    return markdown(
        content, extensions=["smarty", "footnotes", HeideggerIndexExtension()]
    )


RE_LEMMA_LINK = r"\[\[([^\]\n]+)\]\]"  # e.g. [[Aristoteles]]
# For citations were adhering to Pandoc's syntax.
# See https://pandoc.org/chunkedhtml-demo/8.20-citation-syntax.html
RE_WORK_CIT = r"\[@([^\]\n]+?)\]"  # e.g. [@GA-62, p. 4]
RE_IN_TEXT_WORK_CIT = r"(?<!\[)@(\w[^\s,{}]*\w+)|@{([^\n{}]+?)}" # e.g. @GA-29/30 and @{GA 29/30}


class LemmaLinkInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        display_value = m.group(1)
        lemma = m.group(1)
        if "|" in lemma:
            lemma, _, display_value = lemma.rpartition("|")

        try:
            lemma_obj = Lemma.objects.get(sort_key=gen_lemma_sort_key(lemma))
        except Lemma.DoesNotExist:
            el = etree.Element("span")
            print(f"Markdown conversion: link to {lemma} not found")
        else:
            href = reverse("lemma-detail", kwargs={"slug": lemma_obj.slug})
            el = etree.Element("a", href=href)

        el.text = display_value.strip()
        return el, m.start(), m.end()
    
class WorkLinkInlineProcessor(InlineProcessor):
    def build_element(self, work_key, locator, citation=True):
        el = etree.Element("span")
        if citation:
            el.text = "("  # Opening citation
        try:
            work_obj = Work.objects.get(key=work_key)
        except Work.DoesNotExist:
            work_el = etree.SubElement(el, "span")
            print(f"Markdown conversion: cited work {work_key} does not exist")
        else:
            href = reverse("work-detail", kwargs={"slug": work_obj.slug})
            work_el = etree.SubElement(el, "a", href=href)
            if citation:
                work_el.text = work_key
            else:
                work_el.text = work_obj.title

        if locator:
            work_el.tail = f", {locator.strip()}"  # Closing citation
        if citation:
            if work_el.tail:
                work_el.tail += ")"
            else:
                work_el.tail = ")"

        return el
        

class WorkCitationInlineProcessor(WorkLinkInlineProcessor):
    def handleMatch(self, m, data):
        citation = m.group(1)
        if "," in citation:
            work_key, locator = citation.split(",", maxsplit=1)
        else:
            work_key = citation
            locator = ""

        work_key = work_key.strip()
        locator = locator.strip()

        el = self.build_element(work_key, locator, citation=True)

        return el, m.start(), m.end()


class InTextWorkCitInlineProcessor(WorkLinkInlineProcessor):
    def handleMatch(self, m, data):
        if m.group(1):
            work_key = m.group(1)
        else:
            work_key = m.group(2)

        el = self.build_element(work_key, locator="", citation=False)

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
        md.inlinePatterns.register(
            InTextWorkCitInlineProcessor(RE_IN_TEXT_WORK_CIT, md), "work_link", 42
        )
        md.parser.blockprocessors["quote"] = NonLazyBlockQuoteBlockProcessor(md.parser)
