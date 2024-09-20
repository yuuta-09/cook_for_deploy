from django.test import TestCase


# Create your tests here.
class HomeTestCase(TestCase):
    def test_home_view(self):
        """
        ルートパスでトップページが表示されるかをチェックする。
        """
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'homes/top.html')
