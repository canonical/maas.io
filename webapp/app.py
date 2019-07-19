"""
A Flask application for maas.io
"""

import os
import flask

from canonicalwebteam.discourse_docs import DiscourseDocs, DiscourseAPI
from canonicalwebteam.discourse_docs.parsers import DocParser
from canonicalwebteam.flask_base.app import FlaskBase
from canonicalwebteam.templatefinder import TemplateFinder
from canonicalwebteam.search import build_search_view

from webapp.feeds import get_rss_feed


DISCOURSE_BASE_URL = "https://discourse.maas.io/"
DOCS_TOPIC_ID = 25
DOCS_CATEGORY_ID = 5
DOCS_URL_PREFIX = "/docs"
DOCS_TEMPLATE_PATH = "docs/document.html"

app = FlaskBase(
    __name__,
    "maas.io",
    template_folder="../templates",
    static_folder="../static",
)

app.config["SEARCH_API_KEY"] = os.getenv("SEARCH_API_KEY")
app.config["SEARCH_API_URL"] = "https://www.googleapis.com/customsearch/v1"
app.config["SEARCH_CUSTOM_ID"] = "009048213575199080868:i3zoqdwqk8o"

template_finder_view = TemplateFinder.as_view("template_finder")
app.add_url_rule("/", view_func=template_finder_view)
app.add_url_rule("/<path:subpath>", view_func=template_finder_view)

discourse_api = DiscourseAPI(base_url=DISCOURSE_BASE_URL)
discourse_docs = DiscourseDocs(
    api=discourse_api,
    index_topic_id=DOCS_TOPIC_ID,
    category_id=DOCS_CATEGORY_ID,
    document_template=DOCS_TEMPLATE_PATH,
    url_prefix=DOCS_URL_PREFIX,
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

    parser = DocParser(discourse_api, DOCS_TOPIC_ID, DOCS_URL_PREFIX)

    return flask.render_template("docs/api.html", navigation=parser.navigation)
