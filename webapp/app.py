"""
A Flask application for maas.io
"""

import flask

from canonicalwebteam.discourse_docs import DiscourseDocs, DiscourseAPI
from canonicalwebteam.flask_base.app import FlaskBase
from canonicalwebteam.templatefinder import TemplateFinder

from webapp.feeds import get_rss_feed


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
