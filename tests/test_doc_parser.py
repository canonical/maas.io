import json
import unittest
import warnings

from bs4 import BeautifulSoup
import httpretty
import requests

from canonicalwebteam.discourse_docs import DiscourseAPI
from webapp.doc_parser import FastDocParser


class TestFastDocParser(unittest.TestCase):
    def setUp(self):
        # Suppress annoying warnings from HTTPretty
        # See: https://github.com/gabrielfalcao/HTTPretty/issues/368
        warnings.filterwarnings(
            "ignore", category=ResourceWarning, message="unclosed.*"
        )

        # Enable HTTPretty and set up mock URLs
        httpretty.enable()
        self.addCleanup(httpretty.disable)
        self.addCleanup(httpretty.reset)
        # Index page with navigation, URL map and redirects
        httpretty.register_uri(
            httpretty.GET,
            "https://discourse.example.com/t/34.json",
            body=json.dumps(
                {
                    "id": 34,
                    "category_id": 2,
                    "title": "An index page",
                    "slug": "an-index-page",
                    "post_stream": {
                        "posts": [
                            {
                                "id": 3434,
                                "cooked": (
                                    "<p>Some homepage content</p>"
                                    "<h1>Navigation</h1>"
                                    "<ul>"
                                    '<li><a href="/t/page-a/10">Page A</a></li>'
                                    '<li><a href="/t/b-page/12">B page</a></li>'
                                    "</ul>"
                                    "<h1>URLs</h1>"
                                    '<details open="">'
                                    "<summary>Mapping table</summary>"
                                    '<div class="md-table">'
                                    "<table>"
                                    "<thead><tr>"
                                    "<th>Topic</th><th>Path</th></tr></thead>"
                                    "<tbody><tr>"
                                    '<td><a href="https://discourse.example.com/t/'
                                    'page-a/10">Page A</a></td>'
                                    "<td>/a</td>"
                                    "</tr><tr>"
                                    '<td><a href="https://discourse.example.com/t/'
                                    'page-z/26">Page Z</a></td>'
                                    "<td>/page-z</td>"
                                    "</tr></tbody></table>"
                                    "</div></details>"
                                    "<h1>Redirects</h1>"
                                    '<details open="">'
                                    "<summary>Mapping table</summary>"
                                    '<div class="md-table">'
                                    "<table>"
                                    "<thead><tr>"
                                    "<th>Topic</th><th>Path</th></tr></thead>"
                                    "<tbody>"
                                    "<tr><td>/redir-a</td><td>/a</td></tr>"
                                    "<tr>"
                                    "  <td>/example/page</td>"
                                    "  <td>https://example.com/page</td>"
                                    "</tr>"
                                    "</tr></tbody></table>"
                                    "</div></details>"
                                ),
                                "updated_at": "2018-10-02T12:45:44.259Z",
                            }
                        ]
                    },
                }
            ),
            content_type="application/json",
        )

        discourse_api = DiscourseAPI(
            base_url="https://discourse.example.com/",
            session=requests.Session(),
        )

        self.parser = FastDocParser(
            api=discourse_api,
            index_topic_id=34,
            url_prefix="/",
        )
        self.parser.parse()

    def test_index_has_no_nav(self):
        index = self.parser.index_document
        soup = BeautifulSoup(index["body_html"], features="lxml")

        # Check body
        self.assertEqual(soup.p.string, "Some homepage content")

        # Check navigation
        self.assertIsNone(soup.h1)

        # Check URL map worked
        self.assertIsNone(soup.details)
        self.assertNotIn(
            '<a href="/t/page-a/10">Page A</a>',
            soup.decode_contents(),
        )

    def test_nav(self):
        navigation = self.parser.navigation

        self.assertIn(
            '<li><a href="/t/b-page/12">B page</a></li>',
            navigation,
        )

        self.assertIn('<a href="/a">Page A</a>', navigation)

    def test_redirect_map(self):
        self.assertEqual(
            self.parser.redirect_map,
            {"/redir-a": "/a", "/example/page": "https://example.com/page"},
        )

        self.assertEqual(self.parser.warnings, [])

    def test_url_map(self):
        self.assertEqual(
            self.parser.url_map,
            {10: "/a",
             26: "/page-z",
             34: "/",
             "/": 34,
             "/a": 10,
             "/page-z": 26
             }
        )

        self.assertEqual(self.parser.warnings, [])


if __name__ == "__main__":
    unittest.main()
