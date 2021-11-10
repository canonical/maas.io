# Standard library
from canonicalwebteam.discourse_docs import DocParser

import re

# Packages
import dateutil.parser
import humanize
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
        self.index_document = self.parse_topic(index_topic)
        index_soup = BeautifulSoup(
            self.index_document["body_html"], features="lxml"
        )
        self.index_document["body_html"] = str(
            self._get_preamble(index_soup, break_on_title="Navigation")
        )

        # Parse navigation
        self.navigation = self._parse_navigation(raw_index_soup)

        self.metadata = None
        if self.category_id:
            topics = self.get_all_topics_category()
            self.metadata = self._parse_metadata(
                self._replace_links(raw_index_soup, topics)
            )

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

        notification_html = (
            "<div class='{{ notification_class }}'>"
            "<div class='p-notification__response'>"
            "{{ contents | safe }}"
            "</div></div>"
        )

        notification_template = Template(notification_html)
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

                notification = notification_template.render(
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

                notification = notification_template.render(
                    notification_class="p-notification--caution",
                    contents=blockquote.encode_contents().decode("utf-8"),
                )

                blockquote.replace_with(
                    BeautifulSoup(notification, features="lxml")
                )

        return soup

    def _get_preamble(self, soup, break_on_title):
        """
        Given a BeautifulSoup HTML document,
        separate out the HTML at the start, up to
        the heading defined in `break_on_title`,
        and return it as a BeautifulSoup object
        """

        heading = soup.find(re.compile("^h[1-6]$"), text=break_on_title)

        if not heading:
            return soup

        preamble_elements = heading.fetchPreviousSiblings()
        preamble_elements.reverse()
        preamble_html = "".join(map(str, preamble_elements))

        return BeautifulSoup(preamble_html, features="lxml")

    def parse_topic(self, topic):
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

        topic_soup = BeautifulSoup(
            topic["post_stream"]["posts"][0]["cooked"], features="lxml"
        )

        soup = self._process_topic_soup(topic_soup)
        self._replace_lightbox(soup)

        return {
            "title": topic["title"],
            "body_html": str(soup),
            "updated": humanize.naturaltime(
                updated_datetime.replace(tzinfo=None)
            ),
            "topic_path": topic_path,
        }

    def _get_section(self, soup, title_text):
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
        html = str(soup)
        heading = soup.find(HEADER_REGEX, text=title_text)

        if not heading:
            return None

        heading_tag = heading.name
        section_html = html.split(str(heading))[1]

        if f"<{heading_tag}>" in html:
            section_html = section_html.split(f"<{heading_tag}>")[0]

        return BeautifulSoup(section_html, features="lxml")
