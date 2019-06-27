"""
A Flask application for maas.io
"""

import os
import flask

from canonicalwebteam.discourse_docs import DiscourseDocs, DiscourseAPI
from canonicalwebteam.flask_base.app import FlaskBase
from canonicalwebteam.templatefinder import TemplateFinder

from webapp.feeds import get_rss_feed
from webapp.search import get_search_results


DISCOURSE_BASE_URL = "https://discourse.maas.io/"
DOCS_TOPIC_ID = 25
DOCS_CATEGORY_ID = 5
DOCS_URL_PREFIX = "/docs"
DOCS_TEMPLATE_PATH = "docs.html"

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

discourse_docs = DiscourseDocs(
    api=DiscourseAPI(base_url=DISCOURSE_BASE_URL),
    index_topic_id=DOCS_TOPIC_ID,
    category_id=DOCS_CATEGORY_ID,
    document_template="docs.html",
    url_prefix=DOCS_URL_PREFIX,
)
discourse_docs.init_app(app)


@app.errorhandler(404)
def not_found_error(error):
    return flask.render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return flask.render_template("500.html"), 500


@app.context_processor
def context():
    return dict(get_rss_feed=get_rss_feed)


@app.route("/docs/search")
def search():
    """
    Get search results from Google Custom Search
    """
    search_api_key = flask.current_app.config["SEARCH_API_KEY"]
    search_api_url = flask.current_app.config["SEARCH_API_URL"]
    search_custom_id = flask.current_app.config["SEARCH_CUSTOM_ID"]

    query = flask.request.args.get("q")
    num = int(flask.request.args.get("num", "10"))
    start = int(flask.request.args.get("start", "1"))

    context = {"query": query, "start": start, "num": num}

    if query:
        context["results"] = get_search_results(
            search_api_key, search_api_url, search_custom_id, query, start, num
        )

    return flask.render_template("search.html", **context)
