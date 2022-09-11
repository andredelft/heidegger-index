{% load fullurl %}{% load markdownify_filter %}# {% if lemma.type == "w" %}_{% endif %}{{ lemma }}{% if lemma.type == "w" %}_{% endif %}
{% if lemma.type == "w" and lemma.author %}Author: [{{ lemma.author }}]({% fullurl 'index:lemma-detail' lemma.author.slug %})
{% endif %}
{% if lemma.description %}{{ lemma.description | markdownify | safe }}
{% endif %}
## Occurences
See [the index bibliography]({% buildfullurl '/index/#bibliography' %}) for an explanation of the abbreviations used.
{% include 'markdown/_group_by_work.md' with ref_list=lemma.pagereference_set.all %}
{% if works %}{% include 'markdown/_lemma_list.md' with lemma_list=works title="Works by "|add:author_short %}
{% endif %}
{% for child in children %}## {{ child }}
{% if child.description %}{{ child.description | markdownify | safe }}
{% endif %}
{% include 'markdown/_group_by_work.md' with ref_list=child.pagereference_set.all %}
{% endfor %}
{% include 'markdown/_source.md' with type="lemma" %}