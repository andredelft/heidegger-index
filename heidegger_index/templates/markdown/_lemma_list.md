{% if title %}## {{ title }}{% endif %}
{% for lemma in lemma_list %}- [{% if lemma.type == "w" %}_{% endif %}{{ lemma }}{% if lemma.type == "w" %}_{% endif %}](https://heidegger.delve.nu/index{% url 'index:lemma-detail' lemma.slug %})
{% endfor %}
