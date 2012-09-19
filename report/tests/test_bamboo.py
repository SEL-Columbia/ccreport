import os
import unittest

from report.bamboo import bamboo_store_csv_file


class TestBamboo(unittest.TestCase):

    def setUp(self):
        pass

    def test_store_csv_file(self):
        csv_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'fixtures/good_eats.csv'
        )
        dataset_dict = bamboo_store_csv_file(csv_file,
            'http://bamboo.io/datasets')
        self.assertIs(type(dataset_dict), dict)
