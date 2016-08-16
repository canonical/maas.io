<!doctype html>
<html lang="en" dir="ltr">
  {% include "includes/head.html" with css_file="css/docs.css" title="%%TITLE%%" %}

  <body>
    {% include "includes/tag_manager.html" %}

    {% include "includes/header.html" %}

    <div class="wrapper documentation__wrapper">
      <nav class="documentation__nav" id="section-nav">
        <section class="documentation__jump">
          <a href="#">Back to top</a>
        </section>
        {% include "includes/docs_versions.html" %}
        {% include "includes/docs_navigation.html" %}
      </nav>

      {% include "includes/docs_nav_js.html" %}

      <section class="documentation__jump">
        <a href="#section-nav">Jump to section navigation</a>
      </section>

      <main id="main-content" class="inner-wrapper documentation__contents">
        <div class="row">
          %%CONTENT%%
        </div>
      </main>
    </div>

    {% include "includes/footer.html" %}
  </body>

</html>
