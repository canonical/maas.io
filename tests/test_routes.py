import unittest
from webapp.app import app


class TestRoutes(unittest.TestCase):
    def setUp(self):
        """
        Set up Flask app for testing
        """
        app.testing = True
        self.client = app.test_client()

    def test_homepage(self):
        """
        When given the index URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/").status_code, 200)

    def test_not_found(self):
        """
        When given a non-existent URL,
        we should return a 404 status code
        """

        self.assertEqual(self.client.get("/not-found-url").status_code, 404)

    def test_gomod(self):
        """
        When given /core.* with go-get=1 query parameter,
        we should return gomod
        """

        self.assertEqual(self.client.get("/core?go-get=1").status_code, 200)
        self.assertEqual(
            self.client.get("/core/maas?go-get=1").status_code, 200
        )
        self.assertEqual(
            self.client.get("/core/maas/src?go-get=1").status_code, 200
        )

    def test_gomod_not_found(self):
        """
        When given /core.* without go-get=1 query parameter,
        we should return a 404 status code
        """

        self.assertEqual(self.client.get("/core").status_code, 404)
        self.assertEqual(self.client.get("/core/maas").status_code, 404)
        self.assertEqual(self.client.get("/core/maas/src").status_code, 404)
        self.assertEqual(self.client.get("/core/maas?go-get").status_code, 404)
        self.assertEqual(
            self.client.get("/core/maas/src?go-get=0").status_code, 404
        )


if __name__ == "__main__":
    unittest.main()
