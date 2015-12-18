{% extends "base_index.html" %}

{% block page_class %}documentation{% endblock %}
{% block page-title %}| Documentation{% endblock %}

{% block content %}
  <div class="row docs">
    <div class="inner-wrapper">
      <aside class="three-col box docs-nav">
              {% include "docs/_navigation.html" %}
          </aside>
      <div class="nine-col last-col">
        %%CONTENT%%
      </div>
    </div>
  </div>
{% endblock %}

{% block js-extra %}
  <script src="/static/js/nav.js"></script>
{% endblock %}
