"""
A Flask application for maas.io
"""
from datetime import timedelta

import flask
from requests_cache import CachedSession
import talisker.requests

from canonicalwebteam.flask_base.app import FlaskBase
from canonicalwebteam.templatefinder import TemplateFinder
from canonicalwebteam import image_template

from webapp.blog.views import init_blog
from webapp.feeds import get_rss_feed
from webapp.openapi_parser import parse_openapi, read_yaml_from_url
from webapp.views.docs import init_docs
from webapp.views.tutorials import init_tutorials

from http.client import responses

app = FlaskBase(
    __name__,
    "maas.io",
    template_folder="../templates",
    static_folder="../static",
)

template_finder_view = TemplateFinder.as_view("template_finder")
app.add_url_rule("/", view_func=template_finder_view)
app.add_url_rule("/<path:subpath>", view_func=template_finder_view)

docs_session = CachedSession(
    "docs_cache",
    backend="sqlite",
    cache_control=False,
    expire_after=timedelta(days=1),
    allowable_methods=["GET"],
    allowable_codes=[200, 404, 302, 301],
    match_headers=False,
    stale_if_error=True,
)
# talisker-ify the cached session, for metrics, logs etc.
talisker.requests.configure(docs_session)


@app.errorhandler(429)
def too_many_requests(error):
    return (
        flask.render_template("429.html", description=error.description),
        429,
    )


@app.errorhandler(404)
def not_found_error(error):
    return flask.render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return flask.render_template("500.html"), 500


@app.context_processor
def context():
    return {"get_rss_feed": get_rss_feed}


@app.context_processor
def utility_processor():
    return {"image": image_template}


openapi_session = CachedSession(
    "openapi_cache",
    backend="sqlite",
    cache_control=False,
    expire_after=timedelta(days=1),
    allowable_methods=["GET"],
    allowable_codes=[200, 404, 302, 301],
    match_headers=False,
    stale_if_error=True,
)

# talisker-ify the cached session, for metrics, logs etc.
talisker.requests.configure(openapi_session)

docs = init_docs(app, "/docs", session=docs_session)


@app.route("/docs/api")
def api():
    """
    Show the API reference page
    """

    # TODO: Add better caching for this file once the following is complete:
    # https://docs.google.com/document/d/1vCdC7BV53ncOTpWHd2nX5NbwvUH5fDwy-RQGlWpWhXk/edit
    definition_url = (
        "https://raw.githubusercontent.com"
        "/maas/maas-openapi-yaml/main/openapi2.yaml"
    )
    definition = read_yaml_from_url(definition_url, session=openapi_session)
    openapi = parse_openapi(definition)

    docs.parser.parse()
    return flask.render_template(
        "docs/api.html",
        navigation=docs.parser.navigation,
        openapi=openapi,
        responses=responses,
    )


init_blog(app, "/blog")
init_tutorials(app, "/tutorials", session=docs_session)
