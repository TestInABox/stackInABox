import mock

from stackinabox.util import deprecator

from tests.util import base


class TestUtilsDeprecator(base.TestCase):

    def test_basic(self):
        with mock.patch('warnings.warn') as mock_warning:
            old_fn_text = 'apples'
            new_fn_text = 'oranges'
            fn_return = "can't compare them"

            @deprecator.DeprecatedInterface(old_fn_text, new_fn_text)
            def my_deprecated_fn():
                return fn_return

            self.assertEqual(my_deprecated_fn(), fn_return)
            self.assertEqual(mock_warning.call_count, 1)
