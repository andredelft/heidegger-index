# {% if lemma.type == "w" %}_{% endif %}{{ lemma }}{% if lemma.type == "w" %}_{% endif %}
{% if lemma.type == "w" and lemma.author %}Author: [{{ lemma.author }}](https://heidegger.delve.nu/index{% url 'index:lemma-detail' lemma.author.slug %})
{% endif %}
{% if lemma.description_md %}{{ lemma.description_md | safe }}
{% endif %}
## Occurences
See [the index bibliography](https://heidegger.delve.nu/index/#bibliography) for an explanation of the abbreviations used.
{% include 'markdown/_group_by_work.md' with ref_list=lemma.pagereference_set.all %}
{% if works %}{% include 'markdown/_lemma_list.md' with lemma_list=works title="Works by "|add:author_short %}
{% endif %}
{% for child in children %}## {{ child }}
  {% if child.description %}{{ child.description | safe }}
  {% endif %}
  {% include 'markdown/_group_by_work.md' with ref_list=child.pagereference_set.all %}
{% endfor %}
Source: André van Delft and Johannes de Wit, _{{ lemma }} – Heidegger index_ (2022) \<<https://heidegger.delve.nu{% url 'index:lemma-detail' lemma.slug %}>\>.