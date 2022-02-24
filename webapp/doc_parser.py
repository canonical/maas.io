# Standard library
from canonicalwebteam.discourse_docs import DocParser
from canonicalwebteam.discourse_docs.parsers import TOPIC_URL_MATCH

from functools import cached_property
import re
from urllib.parse import urlparse

# Packages
import dateutil.parser
import humanize
import validators
from bs4 import BeautifulSoup, NavigableString
from jinja2 import Template

HEADER_REGEX = re.compile("^h[1-6]$")


class FastDocParser(DocParser):
    def parse(self):
        """
        Get the index topic and split it into:
        - navigation
        - index document content
        - URL map
        - redirects map
        And set those as properties on this object
        """
        index_topic = self.api.get_topic(self.index_topic_id)
        raw_index_soup = BeautifulSoup(
            index_topic["post_stream"]["posts"][0]["cooked"],
            features="lxml",
        )

        # Parse URL & redirects mappings (get warnings)
        self.url_map, url_warnings = self._parse_url_map(raw_index_soup)
        self.redirect_map, redirect_warnings = self._parse_redirect_map(
            raw_index_soup
        )
        self.warnings = url_warnings + redirect_warnings

        # Get body and navigation HTML
        self.index_document = self.parse_topic(
            index_topic, topic_soup=raw_index_soup
        )
        index_soup = self.index_document.pop("body_soup")

        self.index_document["body_html"] = self._get_preamble(
            index_soup, break_on_title="Navigation"
        )

        # Parse navigation
        self.navigation = self._parse_navigation(raw_index_soup)

        self.metadata = None
        if self.category_id:
            topics = self.get_all_topics_category()
            self.metadata = self._parse_metadata(
                self._replace_links(raw_index_soup, topics)
            )

    def _parse_redirect_map(self, index_soup):
        """
        Given the HTML soup of an index topic
        extract the redirect mappings from the "Redirects" section.

        The URLs section should contain a table of
        "Path" to "Location" mappings
        (extra markup around this table doesn't matter)
        e.g.:

        <h1>Redirects</h1>
        <details>
            <summary>Mapping table</summary>
            <table>
            <tr><th>Path</th><th>Location</th></tr>
            <tr>
                <td>/my-funky-path</td>
                <td>/cool-page</td>
            </tr>
            <tr>
                <td>/some/other/path</td>
                <td>https://example.com/cooler-place</td>
            </tr>
            </table>
        </details>

        This will typically be generated in Discourse from Markdown similar to
        the following:

        # Redirects

        [details=Mapping table]
        | Path | Path |
        | -- | -- |
        | /my-funky-path | /cool-page |
        | /some/other/path | https://example.com/cooler-place |
        """

        redirect_soup = self._get_section(index_soup, "Redirects", "details")
        redirect_map = {}
        warnings = []

        if redirect_soup:
            for row in redirect_soup.select("tr:has(td)"):
                path_cell = row.select_one("td:first-child")
                location_cell = row.select_one("td:last-child")

                if not path_cell or not location_cell:
                    warnings.append(
                        f"Could not parse redirect map {path_cell}"
                    )
                    continue

                path = path_cell.text
                location = location_cell.text

                if not path.startswith(self.url_prefix):
                    warnings.append(f"Could not parse redirect map for {path}")
                    continue

                if not (
                    location.startswith(self.url_prefix)
                    or validators.url(location, public=True)
                ):
                    warnings.append(
                        f"Redirect map location {location} is invalid"
                    )
                    continue

                if path in self.url_map:
                    warnings.append(
                        f"Redirect path {path} clashes with URL map"
                    )
                    continue

                redirect_map[path] = location

        return redirect_map, warnings

    def _parse_url_map(self, index_soup):
        """
        Given the HTML soup of an index topic
        extract the URL mappings from the "URLs" section.

        The URLs section should contain a table of
        "Topic" to "Path" mappings
        (extra markup around this table doesn't matter)
        e.g.:

        <h1>URLs</h1>
        <details>
            <summary>Mapping table</summary>
            <table>
            <tr><th>Topic</th><th>Path</th></tr>
            <tr>
                <td><a href="https://forum.example.com/t/page/10">Page</a></td>
                <td>/cool-page</td>
            </tr>
            <tr>
                <td>
                  <a href="https://forum.example.com/t/place/11">Place</a>
                </td>
                <td>/cool-place</td>
            </tr>
            </table>
        </details>

        This will typically be generated in Discourse from Markdown similar to
        the following:

        # URLs

        [details=Mapping table]
        | Topic | Path |
        | -- | -- |
        | https://forum.example.com/t/place/11| /cool-page |
        | https://forum.example.com/t/place/11  | /cool-place |

        """
        url_soup = self._get_section(index_soup, "URLs", "details")

        url_map = {}
        warnings = []

        if url_soup:
            for row in url_soup.tbody("tr"):
                row_contents = row("td")
                topic = row_contents[0]
                path_td = row_contents[-1]
                topic_a = topic.a

                if not topic_a or not path_td:
                    warnings.append("Could not parse URL map item {item}")
                    continue

                topic_url = topic_a.get("href", "")
                topic_path = urlparse(topic_url).path
                topic_match = TOPIC_URL_MATCH.match(topic_path)

                pretty_path = path_td.text

                if not topic_match or not pretty_path.startswith(
                    self.url_prefix
                ):
                    warnings.append("Could not parse URL map item {item}")
                    continue

                topic_id = int(topic_match.groupdict()["topic_id"])

                url_map[pretty_path] = topic_id

        # Add the reverse mappings as well, for efficiency
        ids_to_paths = dict(reversed(pair) for pair in url_map.items())
        url_map.update(ids_to_paths)

        # Add the homepage path
        home_path = self.url_prefix
        if home_path != "/" and home_path.endswith("/"):
            home_path = home_path.rstrip("/")
        url_map[home_path] = self.index_topic_id
        url_map[self.index_topic_id] = home_path

        return url_map, warnings

    @cached_property
    def notification_template(self):
        notification_html = (
            "<div class='{{ notification_class }}'>"
            "<div class='p-notification__response'>"
            "{{ contents | safe }}"
            "</div></div>"
        )

        return Template(notification_html)

    def _replace_notifications(self, soup):
        """
        Given some BeautifulSoup of a document,
        replace blockquotes with the appropriate notification markup.

        E.g. the following Markdown in a Discourse topic:

            > ⓘ Content

        Will generate the following markup, as per the CommonMark spec
        (https://spec.commonmark.org/0.29/#block-quotes):

            <blockquote><p>ⓘ Content</p></blockquote>

        Becomes:

            <div class="p-notification">
                <div class="p-notification__response">
                    <p class="u-no-padding--top u-no-margin--bottom">
                        Content
                    </p>
                </div>
            </div>
        """

        for note_string in soup.findAll(text=re.compile("ⓘ ")):
            first_paragraph = note_string.parent
            blockquote = first_paragraph.parent
            last_paragraph = blockquote.findChildren(recursive=False)[-1]

            if first_paragraph.name == "p" and blockquote.name == "blockquote":
                # Remove extra padding/margin
                first_paragraph.attrs["class"] = "u-no-padding--top"
                if last_paragraph.name == "p":
                    if "class" in last_paragraph.attrs:
                        last_paragraph.attrs["class"] += " u-no-margin--bottom"
                    else:
                        last_paragraph.attrs["class"] = "u-no-margin--bottom"

                # Remove control emoji
                notification_html = blockquote.encode_contents().decode(
                    "utf-8"
                )
                notification_html = re.sub(
                    r"^\n?<p([^>]*)>ⓘ +", r"<p\1>", notification_html
                )

                notification = self.notification_template.render(
                    notification_class="p-notification",
                    contents=notification_html,
                )
                blockquote.replace_with(
                    BeautifulSoup(notification, features="lxml")
                )

        for warning in soup.findAll("img", title=":warning:"):
            first_paragraph = warning.parent
            blockquote = first_paragraph.parent
            last_paragraph = blockquote.findChildren(recursive=False)[-1]

            if first_paragraph.name == "p" and blockquote.name == "blockquote":
                warning.decompose()

                # Remove extra padding/margin
                first_paragraph.attrs["class"] = "u-no-padding--top"
                if last_paragraph.name == "p":
                    if "class" in last_paragraph.attrs:
                        last_paragraph.attrs["class"] += " u-no-margin--bottom"
                    else:
                        last_paragraph.attrs["class"] = "u-no-margin--bottom"

                # Strip leading space
                first_item = last_paragraph.contents[0]
                if isinstance(first_item, NavigableString):
                    first_item.replace_with(first_item.lstrip(" "))

                notification = self.notification_template.render(
                    notification_class="p-notification--caution",
                    contents=blockquote.encode_contents().decode("utf-8"),
                )

                blockquote.replace_with(
                    BeautifulSoup(notification, features="lxml")
                )

        return soup

    def _get_preamble(self, soup, break_on_title):
        """
        Given a BeautifulSoup HTML document, separate out the HTML
        at the start, up to the heading defined in `break_on_title`,
        and return it.
        """

        heading = soup.find(HEADER_REGEX, text=break_on_title)

        if not heading:
            return soup

        return "".join(map(str, reversed(list(heading.previous_siblings))))

    def parse_topic(self, topic, topic_soup=None):
        """
        Parse a topic object from the Discourse API
        and return document data:
        - title: The title
        - body_html: The HTML content of the initial topic post
                        (with some post-processing)
        - updated: A human-readable date, relative to now
                    (e.g. "3 days ago")
        - forum_link: The link to the original forum post
        """
        updated_datetime = dateutil.parser.parse(
            topic["post_stream"]["posts"][0]["updated_at"]
        )

        topic_path = f"/t/{topic['slug']}/{topic['id']}"

        if topic_soup is None:
            topic_soup = BeautifulSoup(
                topic["post_stream"]["posts"][0]["cooked"], features="lxml"
            )

        soup = self._process_topic_soup(topic_soup)
        self._replace_lightbox(soup)

        return {
            "title": topic["title"],
            "body_soup": soup,
            "body_html": str(soup),
            "updated": humanize.naturaltime(
                updated_datetime.replace(tzinfo=None)
            ),
            "topic_path": topic_path,
        }

    def _get_section(self, soup, title_text, content_tag=None):
        """
        Given some HTML soup and the text of a title within it,
        get the content between that title and the next title
        of the same level, and return it as another soup object.

        E.g. if `soup` contains is:

        <p>Pre</p>
        <h2>My heading</h2>
        <p>Content</p>
        <h2>Next heading</h2>

        and `title_text` is "My heading", then it will return:

        <p>Content</p>
        """
        heading = soup.find(HEADER_REGEX, text=title_text)

        if not heading:
            return None

        if content_tag:
            return heading.find_next_sibling(content_tag)
        html = str(soup)
        section_html = html.split(str(heading))[1]

        if f"<{heading.name}>" in html:
            section_html = section_html.split(f"<{heading.name}>")[0]

        return BeautifulSoup(section_html, features="lxml")
