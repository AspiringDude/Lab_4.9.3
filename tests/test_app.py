import unittest
from your_module import geocoding  # adapt to your code

class TestApp(unittest.TestCase):
    def test_geocoding(self):
        status, lat, lng, name = geocoding("Manila", "YOUR_API_KEY")
        self.assertEqual(status, 200)
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lng, float)

if __name__ == "__main__":
    unittest.main()
