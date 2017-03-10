import app
import unittest


class AppTester(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def tearDown(self):
        pass

    def test_list_services(self):
        rv = self.app.get('/')
        print(rv.data)
        assert 'success' in rv.data

    def test_scale_out(self):
        rv = self.app.get('/scale-out')
        print(rv.data)
        assert 'rst' in rv.data

    # def test_scale_in(self):
    #     rv = self.app.get('/scale-in')
    #     print(rv.data)
    #     assert 'rst' in rv.data

if __name__ == '__main__':
    unittest.main()