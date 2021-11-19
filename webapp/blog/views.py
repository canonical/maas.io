import flask
import talisker

from canonicalwebteam.blog import (
    BlogViews,
    BlogAPI,
    build_blueprint,
)
from dateutil import parser


def init_blog(app, url_prefix):
    session = talisker.requests.get_session()
    blog_api = BlogAPI(
        session=session,
        thumbnail_width=354,
        thumbnail_height=199,
    )
    blog = build_blueprint(
        BlogViews(
            api=blog_api,
            blog_title="MAAS Blog",
            tag_ids=[1304],
            excluded_tags=[3184, 3265, 3408],
        )
    )

    @blog.context_processor
    def add_newsletter():
        newsletter_subscribed = flask.request.args.get(
            "newsletter", default=False, type=bool
        )

        return {"newsletter_subscribed": newsletter_subscribed}

    @blog.route("/sitemap.xml")
    def sitemap():
        base_url = "https://maas.io/blog"
        links = []
        page = 1
        while True:
            url = (
                f"https://ubuntu.com/blog/wp-json/wp/v2/posts?"
                f"tags=1304&per_page=100&page={page}"
                f"&tags_exclude=3184%2C3265%2C3408"
            )

            response = session.get(url)
            if response.status_code == 400:
                break

            try:
                blog_response = response.json()
            except Exception:
                continue

            for post in blog_response:
                try:
                    date = (
                        parser.parse(post["date"])
                        .replace(tzinfo=None)
                        .strftime("%Y-%m-%d")
                    )
                    links.append(
                        {
                            "url": base_url + "/" + post["slug"],
                            "last_udpated": date,
                        }
                    )
                except Exception:
                    continue

            page = page + 1

        xml_sitemap = flask.render_template(
            "sitemap/sitemap.xml",
            base_url=base_url,
            links=links,
        )

        response = flask.make_response(xml_sitemap)
        response.headers["Content-Type"] = "application/xml"
        response.headers["Cache-Control"] = "public, max-age=43200"

        return response

    app.register_blueprint(blog, url_prefix=url_prefix)
