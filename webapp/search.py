from canonicalwebteam.http import CachedSession


SEARCH_SESSION = CachedSession(fallback_cache_duration=600)


class NoAPIKeyError(Exception):
    pass


def get_search_results(
    api_key,
    api_url,
    search_custom_id,
    query,
    start,
    num,
    session=SEARCH_SESSION,
):
    """
    Query the Google Custom Search API for search results
    """
    if not api_key:
        raise NoAPIKeyError("Unable to search: No API key provided")

    results = session.get(
        api_url,
        params={
            "key": api_key,
            "cx": search_custom_id,
            "q": query,
            "siteSearch": "maas.io/docs",
            "start": start,
            "num": num,
        },
    ).json()

    if "items" in results:
        # Move "items" to "entries" as "items" is a method name for dicts
        # and it causes wierd things to happen in Jinja2
        results["entries"] = results.pop("items")
        for item in results["entries"]:
            item["htmlSnippet"] = item["htmlSnippet"].replace("<br>\n", "")

    return results
