<!doctype html>
<html lang="en" dir="ltr">
  {% include "includes/head.html" with css_file="css/docs.css" title="%%TITLE%%" %}

  <body class="documentation">
    {% include "includes/tag_manager.html" %}

    {% include "includes/header.html" %}

    <div class="wrapper">
      <nav class="documentation__nav">
        {% include "includes/docs_navigation.html" %}
      </nav>

      {% include "includes/docs_nav_js.html" %}

      <main id="main-content" class="inner-wrapper">
        <div class="row">
          %%CONTENT%%
        </div>
      </main>
      <aside class="toc">
      </aside>
    </div>

    {% include "includes/footer.html" %}
  </body>

</html>
