# Index of {{ work.csl_json.title }}

## Work reference
{{ reference_md | safe }}

## Index terms
{% include 'markdown/_group_by_lemma.md' with ref_list=term_list %}
{% if person_list %}{% include 'markdown/_group_by_lemma.md' with ref_list=person_list group_title="People mentioned" %}{% endif %}
{% if work_list %}{% include 'markdown/_group_by_lemma.md' with ref_list=work_list group_title="Works mentioned" %}{% endif %}

{% include 'markdown/_source.md' with type='work' %}