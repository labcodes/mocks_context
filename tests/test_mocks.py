from unittest import TestCase
from unittest.mock import patch, call

from mocks_context.mocks import MockedFunction
from mocks_context.expectations import SingleCallExpectation, MultipleCallsExpectation, NoCallsExpectation


class MockedFunctionTests(TestCase):

    def setUp(self):
        self.mock = MockedFunction('objects.function')

    def tearDown(self):
        self.mock.release()

    def test_set_output(self):
        ret = self.mock.set_output(42)

        assert ret == self.mock
        assert self.mock.mock.return_value == 42

    def test_set_many_outputs(self):
        results = [42, 24, 50]
        ret = self.mock.set_many_outputs(results)

        assert ret == self.mock
        assert list(self.mock.mock.side_effect) == results

    def test_expect_single_call(self):
        ret = self.mock.expect_single_call(10, 20, c=30, d=40)

        expectation = self.mock.all_expectations()[0]
        assert isinstance(expectation, SingleCallExpectation)

        assert ret == self.mock
        assert expectation.mocked_method == self.mock.mock
        assert expectation.call_args == (10, 20)
        assert expectation.call_kwargs == {'c': 30, 'd': 40}

    def test_expect_call(self):
        ret = self.mock.expect_call(10, 20, c=30, d=40)
        ret = self.mock.expect_call(50, 60, c=70, d=80)

        expectation = self.mock.all_expectations()[0]
        assert isinstance(expectation, MultipleCallsExpectation)

        assert ret == self.mock
        assert expectation.mocked_method == self.mock.mock
        assert expectation.any_order is False
        assert expectation.match_count is False
        assert expectation.count == 2
        assert call(10, 20, c=30, d=40) in expectation._calls
        assert call(50, 60, c=70, d=80) in expectation._calls

    def test_expect_match_call_count(self):
        self.mock.expect_call(10, 20, c=30, d=40)
        self.mock.expect_call(50, 60, c=70, d=80)
        ret = self.mock.expect_match_call_count()

        expectation = self.mock.all_expectations()[0]
        assert isinstance(expectation, MultipleCallsExpectation)

        assert ret == self.mock
        assert expectation.mocked_method == self.mock.mock
        assert expectation.match_count is True
        assert expectation.count == 2

    def test_expect_match_call_count_overwrite_count(self):
        self.mock.expect_call(10, 20, c=30, d=40)
        self.mock.expect_call(50, 60, c=70, d=80)
        ret = self.mock.expect_match_call_count(20)

        expectation = self.mock.all_expectations()[0]
        assert isinstance(expectation, MultipleCallsExpectation)

        assert ret == self.mock
        assert expectation.mocked_method == self.mock.mock
        assert expectation.match_count is True
        assert expectation.count == 20

    def test_expect_match_call_count_do_not_require_calls_config(self):
        ret = self.mock.expect_match_call_count()

        expectation = self.mock.all_expectations()[0]
        assert isinstance(expectation, MultipleCallsExpectation)

        assert ret == self.mock
        assert expectation.mocked_method == self.mock.mock
        assert expectation.match_count is True
        assert expectation.count == 0

    def test_expect_no_calls(self):
        ret = self.mock.expect_no_calls()

        expectation = self.mock.all_expectations()[0]
        assert isinstance(expectation, NoCallsExpectation)

        assert ret == self.mock
        assert expectation.mocked_method == self.mock.mock

    def test_mocked_function_can_have_only_a_sigle_expectation(self):
        ret = self.mock.expect_no_calls()
        ret = self.mock.expect_call(10, 20, c=30, d=40)
        ret = self.mock.expect_single_call(50, 60, c=70, d=80)

        expectations = self.mock.all_expectations()

        assert 1 == len(expectations)
        assert isinstance(expectations[0], SingleCallExpectation)
