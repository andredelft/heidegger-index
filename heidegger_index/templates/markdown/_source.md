Source:
André van Delft and Johannes de Wit, _{% if type == 'work' %}{{ work.title }} – Heidegger index_, \<<https://heidegger.delve.nu{% url 'index:work-detail' work.slug %}>\>,
{% elif type == 'lemma' %}{{ lemma }} – Heidegger index_, \<<https://heidegger.delve.nu{% url 'index:lemma-detail' lemma.slug %}>\>,{% endif %} accessed on {% now "j/n/Y" %}.