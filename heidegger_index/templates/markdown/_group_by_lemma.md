{% if group_title %}
### {{ group_title|safe }}
{% endif %}
{% regroup ref_list by lemma as lemma_groups %}
{% for lemma, page_ref_list in lemma_groups %}
- {% if lemma.type == "w" %}_{% endif %}{{ lemma }}{% if lemma.type == "w" %}_{% endif %}: {{ page_ref_list|join:', ' }}
{% endfor %}