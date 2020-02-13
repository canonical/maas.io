"""
A Flask application for maas.io
"""

import flask
import math

from canonicalwebteam.discourse_docs import (
    DiscourseDocs,
    DocParser,
    DiscourseAPI,
)
from canonicalwebteam.flask_base.app import FlaskBase
from canonicalwebteam.templatefinder import TemplateFinder
from canonicalwebteam.search import build_search_view
from canonicalwebteam import image_template

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
    category_id=5,
    url_prefix="/docs",
)
if app.debug:
    doc_parser.api.session.adapters["https://"].timeout = 99
discourse_docs = DiscourseDocs(
    parser=doc_parser,
    document_template="docs/document.html",
    url_prefix="/docs",
)
discourse_docs.init_app(app)


# Search
app.add_url_rule(
    "/docs/search",
    "docs-search",
    build_search_view(site="maas.io/docs", template_path="docs/search.html"),
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


@app.context_processor
def utility_processor():
    return {"image": image_template}


@app.route("/docs/api")
def api():
    """
    Show the static api page
    """

    doc_parser.parse()
    return flask.render_template(
        "docs/api.html", navigation=doc_parser.navigation
    )


url_prefix = "/tutorials"
tutorials_docs_parser = DocParser(
    api=DiscourseAPI(base_url="https://discourse.maas.io/"),
    category_id=16,
    index_topic_id=1289,
    url_prefix=url_prefix,
)
tutorials_docs = DiscourseDocs(
    parser=tutorials_docs_parser,
    document_template="/tutorials/tutorial.html",
    url_prefix=url_prefix,
    blueprint_name="tutorials",
)


@app.route(url_prefix)
def index():
    page = flask.request.args.get("page", default=1, type=int)
    topic = flask.request.args.get("topic", default=None, type=str)
    sort = flask.request.args.get("sort", default=None, type=str)
    posts_per_page = 15
    tutorials_docs.parser.parse()
    if not topic:
        metadata = tutorials_docs.parser.metadata
    else:
        metadata = [
            doc
            for doc in tutorials_docs.parser.metadata
            if topic in doc["categories"]
        ]

    if sort == "difficulty-desc":
        metadata = sorted(
            metadata, key=lambda k: k["difficulty"], reverse=True
        )

    if sort == "difficulty-asc" or not sort:
        metadata = sorted(
            metadata, key=lambda k: k["difficulty"], reverse=False
        )

    total_pages = math.ceil(len(metadata) / posts_per_page)

    return flask.render_template(
        "tutorials/index.html",
        navigation=tutorials_docs.parser.navigation,
        forum_url=tutorials_docs.parser.api.base_url,
        metadata=metadata,
        page=page,
        topic=topic,
        sort=sort,
        posts_per_page=posts_per_page,
        total_pages=total_pages,
    )


tutorials_docs.init_app(app)
