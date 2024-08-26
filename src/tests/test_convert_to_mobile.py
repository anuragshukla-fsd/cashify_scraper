import unittest
from utils import convert_to_mobile
from constants import VENDOR_ID, DEFAULT_WARRANTY, DEFAULT_CONDITION, DEFAULT_TYPE

class TestConvertToMobile(unittest.TestCase):

    def test_basic_conversion(self):
        brand = "Samsung"
        model = "Galaxy S21"
        variant = "Galaxy S21 (256 GB, 8 GB RAM)"
        link = "http://example.com/samsung-galaxy-s21"
        price = "₹79,999"

        mobile = convert_to_mobile(brand, model, variant, link, price)

        self.assertEqual(mobile.make, "Samsung")
        self.assertEqual(mobile.model_name, "Galaxy S21")
        self.assertEqual(mobile.ram, 8)
        self.assertEqual(mobile.storage, 256)
        self.assertEqual(mobile.price, 79999)
        self.assertEqual(mobile.actualPrice, 79999)
        self.assertEqual(mobile.link, "http://example.com/samsung-galaxy-s21")
        self.assertEqual(mobile.vendor_id, VENDOR_ID)
        self.assertEqual(mobile.warranty, DEFAULT_WARRANTY)
        self.assertEqual(mobile.mobiru_condition, DEFAULT_CONDITION)
        self.assertEqual(mobile.type, DEFAULT_TYPE)
        self.assertFalse(mobile.storageInTB)

    def test_storage_in_tb(self):
        brand = "Apple"
        model = "iPhone 12"
        variant = "Iphone 12 (1 TB)"
        link = "http://example.com/iphone-12"
        price = "₹1,29,999"

        mobile = convert_to_mobile(brand, model, variant, link, price)

        self.assertEqual(mobile.storage, 1)
        self.assertEqual(mobile.ram, "--")
        self.assertTrue(mobile.storageInTB)

    def test_price_conversion(self):
        brand = "Google"
        model = "Pixel 5"
        variant = "8 GB RAM, 128 GB"
        link = "http://example.com/pixel-5"
        price = "₹69,999"

        mobile = convert_to_mobile(brand, model, variant, link, price)

        self.assertEqual(mobile.price, 69999)
        self.assertEqual(mobile.actualPrice, 69999)

    def test_price_conversion_no_comma(self):
        brand = "Google"
        model = "Pixel 5"
        variant = "8 GB RAM, 128 GB"
        link = "http://example.com/pixel-5"
        price = "₹69999"

        mobile = convert_to_mobile(brand, model, variant, link, price)

        self.assertEqual(mobile.price, 69999)
        self.assertEqual(mobile.actualPrice, 69999)

if __name__ == '__main__':
    unittest.main()

