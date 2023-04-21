from os import getenv

from canonicalwebteam.discourse import (
    DiscourseAPI,
    DocParser,
    Docs,
)
from canonicalwebteam.search import build_search_view

DISCOURSE_API_KEY = getenv("DISCOURSE_API_KEY")
DISCOURSE_API_USERNAME = getenv("DISCOURSE_API_USERNAME")


def init_docs(app, url_prefix: str, session) -> Docs:
    """Initialise Docs attaching to Discourse."""
    discourse_docs = Docs(
        parser=DocParser(
            api=DiscourseAPI(
                base_url="https://discourse.maas.io/",
                session=session,
                api_key=DISCOURSE_API_KEY,
                api_username=DISCOURSE_API_USERNAME,
                get_topics_query_id=2,
            ),
            index_topic_id=6662,
            url_prefix=url_prefix,
            tutorials_index_topic_id=1289,
            tutorials_url_prefix="/tutorials",
        ),
        document_template="docs/document.html",
        url_prefix=url_prefix,
    )
    discourse_docs.init_app(app)

    app.add_url_rule(
        "/docs/search",
        "docs-search",
        build_search_view(
            session=session,
            site="maas.io/docs",
            template_path="docs/search.html",
        ),
    )
    return discourse_docs
