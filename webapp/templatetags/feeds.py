from django import template
from webapp.lib.feeds import get_json_feed_content, get_rss_feed_content

register = template.Library()


@register.assignment_tag
def get_json_feed(feed_url, limit=3, **kwargs):
    return get_json_feed_content(feed_url, limit=limit, **kwargs)


@register.assignment_tag
def get_rss_feed(feed_url, limit=3, **kwargs):
    return get_rss_feed_content(feed_url, limit=limit, **kwargs)
