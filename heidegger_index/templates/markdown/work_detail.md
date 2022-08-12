# Index of {{ work.csl_json.title }}
Generated from:
André van Delft and Johannes de Wit, _Heidegger index_ (2022) <https://heidegger.delve.nu{% url 'index:work-detail' work.slug %}>.

{# TODO: Clear up HTML in the work.reference #}
## Reference
{{ work.reference | safe }}

{# TODO: Clear up whitespace in between list items #}
## Index terms
{% include 'markdown/_group_by_lemma.md' with ref_list=term_list %}
{% if person_list %}
  {% include 'markdown/_group_by_lemma.md' with ref_list=person_list group_title="People mentioned" %}
{% endif %}
{% if work_list %}
  {% include 'markdown/_group_by_lemma.md' with ref_list=work_list group_title="Works mentioned" %}
{% endif %}
