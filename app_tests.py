import app
import unittest


class AppTester(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def tearDown(self):
        super().tearDown()

    def test_list_services(self):
        rv = self.app.get('/')
        print(rv.data)
        assert 'success' in rv.data

    # def test_scale_out(self):
    #     rv = self.app.get('/scale-out')
    #     assert 'rst' in rv.data

if __name__ == '__main__':
    unittest.main()