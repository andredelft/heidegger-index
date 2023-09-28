{% load fullurl %}{% if group_title %}### {{ group_title|safe }}{% endif %}{% regroup ref_list by work as work_groups %}
{% for work, page_refs in work_groups %}- {% if work.reference %}[{{ work }}]({% fullurl 'work-detail' work.slug %}){% else %}{{ work }}{% endif %}: {{ page_refs|join:', ' }}
{% endfor %}
