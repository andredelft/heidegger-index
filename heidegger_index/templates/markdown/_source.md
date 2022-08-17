Source:
André van Delft and Johannes de Wit, '{% if type == 'work' %}{{ work.title }}', in _Heidegger index_ (n.d.) \<<https://heidegger.delve.nu{% url 'index:work-detail' work.slug %}>\>,
{% elif type == 'lemma' %}{{ lemma }}', in _Heidegger index_, \<<https://heidegger.delve.nu{% url 'index:lemma-detail' lemma.slug %}>\>{% endif %} [accessed {% now "j F Y" %}].