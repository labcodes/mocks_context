import pytest
from unittest import TestCase
from unittest.mock import Mock

from mocks_context.expectations import SingleCallExpectation, MultipleCallsExpectation, NoCallsExpectation


def assert_satisfied(expectation):
    assert expectation.satisfied() is None

def assert_not_satisfied(expectation):
    with pytest.raises(AssertionError):
        expectation.satisfied()


class SingleCallExpectationTests(TestCase):

    def setUp(self):
        self.mocked_method = Mock()
        self.expectation = SingleCallExpectation(self.mocked_method, 1, 2, b=3, c=4)

    def test_successful_single_call_expectation(self):
        self.mocked_method(1, 2, b=3, c=4)
        assert_satisfied(self.expectation)

    def test_error_on_single_call_expectation_due_to_missing_arg(self):
        self.mocked_method(1, b=3, c=4)
        assert_not_satisfied(self.expectation)

    def test_error_on_single_call_expectation_due_to_extra_arg(self):
        self.mocked_method(1, 2, 40, b=3, c=4)
        assert_not_satisfied(self.expectation)

    def test_error_on_single_call_expectation_due_to_incorrect_arg(self):
        self.mocked_method(10, 20, b=3, c=4)
        assert_not_satisfied(self.expectation)

    def test_error_on_single_call_expectation_due_to_missing_kwarg(self):
        self.mocked_method(1, 2, b=3)
        assert_not_satisfied(self.expectation)

    def test_error_on_single_call_expectation_due_to_incorrect_kwarg(self):
        self.mocked_method(10, 20, b=30, c=40)
        assert_not_satisfied(self.expectation)

    def test_error_on_single_call_expectation_due_to_extra_kwarg(self):
        self.mocked_method(1, 2, b=3, c=4, d=1000)
        assert_not_satisfied(self.expectation)


class MultipleCallsExpectationTests(TestCase):

    def setUp(self):
        self.mocked_method = Mock()
        self.expectation = MultipleCallsExpectation(self.mocked_method)

    def test_successful_multiple_calls_expectation(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=4)
        self.mocked_method(4, 3, b=2, c=1)

        assert_satisfied(self.expectation)

    def test_multiple_calls_expectation_ensure_order_by_default(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        # calls in a different order from the expectations
        self.mocked_method(4, 3, b=2, c=1)
        self.mocked_method(1, 2, b=3, c=4)

        assert_not_satisfied(self.expectation)

        self.expectation.any_order = True
        assert_satisfied(self.expectation)

    def test_successful_multiple_calls_ensuring_expected_calls_count(self):
        self.expectation.match_count = True
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=4)
        self.mocked_method(4, 3, b=2, c=1)

        assert_satisfied(self.expectation)

        # extra call should fail
        self.mocked_method(4, 3, b=2, c=1)
        assert_not_satisfied(self.expectation)

    def test_successful_multiple_calls_ensuring_forced_call_count(self):
        self.expectation.match_count = True
        self.expectation.count = 10
        self.expectation.new_call_params(1, 2, b=3, c=4)

        for i in range(10):
            self.mocked_method(1, 2, b=3, c=4)

        assert self.expectation.satisfied() is None
        assert_satisfied(self.expectation)

        # extra call should fail
        self.mocked_method(1, 2, b=3, c=4)
        assert_not_satisfied(self.expectation)

    def test_error_on_multiple_call_expectation_due_to_missing_arg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=4)
        self.mocked_method(4, b=2, c=1)

        assert_not_satisfied(self.expectation)

    def test_error_on_multiple_call_expectation_due_to_extra_arg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(100, 1, 2, b=3, c=4)
        self.mocked_method(4, 3, b=2, c=1)

        assert_not_satisfied(self.expectation)

    def test_error_on_multiple_call_expectation_due_to_incorrect_arg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=4)
        self.mocked_method(50, 3, b=2, c=1)

        assert_not_satisfied(self.expectation)

    def test_error_on_multiple_call_expectation_due_to_missing_kwarg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3)
        self.mocked_method(4, 3, b=2, c=1)

        assert_not_satisfied(self.expectation)

    def test_error_on_multiple_call_expectation_due_to_incorrect_kwarg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=1000)
        self.mocked_method(4, 3, b=2, c=1)

        assert_not_satisfied(self.expectation)

    def test_error_on_multiple_call_expectation_due_to_extra_kwarg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=4)
        self.mocked_method(4, 3, b=2, c=1, f=10)

        assert_not_satisfied(self.expectation)


class NoCallsExpectationTests(TestCase):

    def setUp(self):
        self.mocked_method = Mock()
        self.expectation = NoCallsExpectation(self.mocked_method)

    def test_successful_no_calls_expectation(self):
        assert_satisfied(self.expectation)

    def test_no_calls_expectation_fails_if_any_call(self):
        self.mocked_method(1, 2, b=3, c=4)
        assert_not_satisfied(self.expectation)
