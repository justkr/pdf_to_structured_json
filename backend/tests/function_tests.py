import unittest
import pandas as pd
import pandas.testing as pd_testing
import os
import sys

sys.path.append(os.path.dirname(sys.path[0]))

# Importing functions
from app.functions import get_dominant_font

class Testing(unittest.TestCase):

    # Set up to be able to compare dataframes
    def assertDataframeEqual(self, a, b, msg):
        try:
            pd_testing.assert_frame_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def setUp(self):
        self.addTypeEqualityFunc(pd.DataFrame, self.assertDataframeEqual)

    def test_get_dominant_font_diff_font_same_size(self):

        # Table with one font different than other but with the same size as other
        chars_details = pd.DataFrame()
        chars_details['FontName'] = ['Font1','Font1','Font1','Font1','Font1','Font1bold','Font1','Font1','Font1','Font1']
        chars_details['FontSize'] = [1] * 10
        chars_details['FontSColor'] = ['(0, 0, 0, 0.6)'] * 10

        # Applying function
        chars_details = get_dominant_font(chars_details)

        # Table that we want to get
        chars_details_correct = pd.DataFrame()
        chars_details_correct['FontName'] = ['Font1'] * 10
        chars_details_correct['FontSize'] = [1] * 10
        chars_details_correct['FontSColor'] = ['(0, 0, 0, 0.6)'] * 10

        self.assertEqual(chars_details, chars_details_correct)

    def test_get_dominant_font_diff_font_diff_size(self):

        # Table with one font and size different than other
        chars_details = pd.DataFrame()
        chars_details['FontName'] = ['Font1','Font1','Font1','Font1','Font1','Font1bold','Font1','Font1','Font1','Font1']
        chars_details['FontSize'] = [1] * 4 + [2] + [1] * 5
        chars_details['FontSColor'] = ['(0, 0, 0, 0.6)'] * 10

        # Applying function
        chars_details = get_dominant_font(chars_details)

        # Table that we want to get
        chars_details_correct = pd.DataFrame()
        chars_details_correct['FontName'] = ['Font1'] * 10
        chars_details_correct['FontSize'] = [1] * 10
        chars_details_correct['FontSColor'] = ['(0, 0, 0, 0.6)'] * 10

        self.assertEqual(chars_details, chars_details_correct)

    def test_get_dominant_font_empty_table(self):

        # Empty table with nothing to change
        chars_details = pd.DataFrame()

        # Applying function - nothing should be changed
        chars_details = get_dominant_font(chars_details)

        self.assertEqual(chars_details, chars_details)

    def test_get_dominant_font_same_font_diff_size(self):

        # Table with the same font but different size
        chars_details = pd.DataFrame()
        chars_details['FontName'] = ['Font1'] * 10
        chars_details['FontSize'] = [1] * 4 + [2] + [1] * 5
        chars_details['FontSColor'] = ['(0, 0, 0, 0.6)'] * 10

        # Applying function - nothing should be changed
        chars_details = get_dominant_font(chars_details)

        # Table that we want to get
        chars_details_correct = pd.DataFrame()
        chars_details_correct['FontName'] = ['Font1'] * 10
        chars_details_correct['FontSize'] = [1] * 10
        chars_details_correct['FontSColor'] = ['(0, 0, 0, 0.6)'] * 10

        self.assertEqual(chars_details, chars_details_correct)

if __name__ == '__main__':

    unittest.main()