{% load fullurl %}Source:
André van Delft and Johannes de Wit, '{% if type == 'work' %}{{ work.title }}', in _Heidegger index_ (n.d.) \<<{% fullurl 'work-detail' work.slug %}>\>,
{% elif type == 'lemma' %}{{ lemma }}', in _Heidegger index_ (n.d.), \<<{% fullurl 'lemma-detail' lemma.slug %}>\>{% endif %} [accessed {% now "j F Y" %}].