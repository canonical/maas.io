"""
A Flask application for maas.io
"""

import flask

from canonicalwebteam.discourse_docs import (
    DiscourseDocs,
    DocParser,
    DiscourseAPI,
)
from canonicalwebteam.flask_base.app import FlaskBase
from canonicalwebteam.templatefinder import TemplateFinder
from canonicalwebteam.search import build_search_view

from webapp.feeds import get_rss_feed


app = FlaskBase(
    __name__,
    "maas.io",
    template_folder="../templates",
    static_folder="../static",
)

template_finder_view = TemplateFinder.as_view("template_finder")
app.add_url_rule("/", view_func=template_finder_view)
app.add_url_rule("/<path:subpath>", view_func=template_finder_view)

doc_parser = DocParser(
    api=DiscourseAPI(base_url="https://discourse.maas.io/"),
    index_topic_id=25,
    url_prefix="/docs",
)
if app.debug:
    doc_parser.api.session.adapters["https://"].timeout = 99
discourse_docs = DiscourseDocs(
    parser=doc_parser,
    document_template="docs/document.html",
    category_id=5,
    url_prefix="/docs",
)
discourse_docs.init_app(app)


# Search
app.add_url_rule(
    "/docs/search",
    "docs-search",
    build_search_view(site="docs.maas.io", template_path="docs/search.html"),
)


@app.errorhandler(404)
def not_found_error(error):
    return flask.render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return flask.render_template("500.html"), 500


@app.context_processor
def context():
    return dict(get_rss_feed=get_rss_feed)


@app.route("/docs/api")
def api():
    """
    Show the static api page
    """

    doc_parser.parse()
    return flask.render_template(
        "docs/api.html", navigation=doc_parser.navigation
    )
