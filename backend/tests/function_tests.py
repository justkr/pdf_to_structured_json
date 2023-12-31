import unittest
import pandas as pd
import pandas.testing as pd_testing
import os
import sys

sys.path.append(os.path.dirname(sys.path[0]))

# Importing functions
from app.functions import get_main_font_among_pages, group_lines_into_page

class Testing(unittest.TestCase):

    # Set up to be able to compare dataframes
    def assertDataframeEqual(self, a, b, msg):
        try:
            pd_testing.assert_frame_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def setUp(self):
        self.addTypeEqualityFunc(pd.DataFrame, self.assertDataframeEqual)

    def test_get_main_font_among_pages(self):

        # Table with details
        fonts = pd.DataFrame()
        fonts['FontName'] = ['A', 'B', 'B', 'A', 'C', 'B']
        fonts['FontSize'] = [1, 2, 3, 1, 4, 2]
        fonts['FontSColor'] = ['a', 'a', 'a', 'a', 'c', 'a']
        fonts['ElementText'] = ['ertg', 'sedrtgfhyjnbvd', 'ertghgb', 'drf', 'c', 'wesddfghtr']

        # Applying function
        func_main_font = get_main_font_among_pages([fonts, fonts, fonts])

        self.assertEqual(func_main_font['FontName'], 'B')
        self.assertEqual(func_main_font['FontSize'], 2)
        self.assertEqual(func_main_font['FontSColor'], 'a')

    def test_group_lines_into_page(self):

        line_details = pd.DataFrame()
        line_details['ElementText'] = ['A', 'B', 'C', 'a', 'b', 'c']
        line_details['FontName'] = ['A1', 'A1', 'A1', 'A2', 'A2', 'A2']
        line_details['FontSize'] = [1, 1, 1, 2, 2, 2]
        line_details['FontSColor'] = ['a', 'a', 'a', 'b', 'b', 'b']

        page_details_test = group_lines_into_page(line_details)

        page_details = pd.DataFrame()
        page_details['ElementText'] = ['A B C', 'a b c']
        page_details['FontName'] = ['A1', 'A2']
        page_details['FontSize'] = [1, 2]
        page_details['FontSColor'] = ['a', 'b']

        self.assertEqual(page_details_test, page_details)

if __name__ == '__main__':

    unittest.main()