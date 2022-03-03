import unittest
from webapp.app import app, docs_session


class TestCacheClear(unittest.TestCase):
    def setUp(self):
        """
        Set up Flask app for testing
        """
        app.testing = True
        self.client = app.test_client()

    def test_cache_clear(self):
        """
        When given the index URL,
        we should return a 200 status code
        """
        docs_session.get("http://httpbin.org/get")
        self.assertCountEqual(
            docs_session.cache.urls, ["http://httpbin.org/get"]
        )
        response = self.client.get("/docs/_cache_clear")
        self.assertRegex(
            response.get_data(as_text=True),
            r"OK, all 1 URL\(s\) ☢🚀 from the cache",
        )
        self.assertEqual(response.status_code, 410)
        self.assertCountEqual(docs_session.cache.urls, [])
