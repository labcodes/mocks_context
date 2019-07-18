import pytest
from unittest import TestCase
from unittest.mock import Mock

from mocks_context.expectations import SingleCallExpectation, MultipleCallsExpectation, NoCallsExpectation


class SingleCallExpectationTests(TestCase):

    def setUp(self):
        self.mocked_method = Mock()
        self.expectation = SingleCallExpectation(self.mocked_method, 1, 2, b=3, c=4)

    def test_successful_single_call_expectation(self):
        self.mocked_method(1, 2, b=3, c=4)
        assert self.expectation.satisfied() is None

    def test_error_on_single_call_expectation_due_to_missing_arg(self):
        self.mocked_method(1, b=3, c=4)
        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_error_on_single_call_expectation_due_to_extra_arg(self):
        self.mocked_method(1, 2, 40, b=3, c=4)
        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_error_on_single_call_expectation_due_to_incorrect_arg(self):
        self.mocked_method(10, 20, b=3, c=4)
        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_error_on_single_call_expectation_due_to_missing_kwarg(self):
        self.mocked_method(1, 2, b=3)
        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_error_on_single_call_expectation_due_to_incorrect_kwarg(self):
        self.mocked_method(10, 20, b=30, c=40)
        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_error_on_single_call_expectation_due_to_extra_kwarg(self):
        self.mocked_method(1, 2, b=3, c=4, d=1000)
        with pytest.raises(AssertionError):
            self.expectation.satisfied()


class MultipleCallsExpectationTests(TestCase):

    def setUp(self):
        self.mocked_method = Mock()
        self.expectation = MultipleCallsExpectation(self.mocked_method)

    def test_successful_multiple_calls_expectation(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=4)
        self.mocked_method(4, 3, b=2, c=1)

        assert self.expectation.satisfied() is None

    def test_multiple_calls_expectation_ensure_order_by_default(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        # calls in a different order from the expectations
        self.mocked_method(4, 3, b=2, c=1)
        self.mocked_method(1, 2, b=3, c=4)

        with pytest.raises(AssertionError):
            assert self.expectation.satisfied()

        self.expectation.any_order = True
        assert self.expectation.satisfied() is None

    def test_successful_multiple_calls_ensuring_expected_calls_count(self):
        self.expectation.match_count = True
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=4)
        self.mocked_method(4, 3, b=2, c=1)

        assert self.expectation.satisfied() is None

        # extra call should fail
        self.mocked_method(4, 3, b=2, c=1)
        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_successful_multiple_calls_ensuring_forced_call_count(self):
        self.expectation.match_count = True
        self.expectation.count = 10
        self.expectation.new_call_params(1, 2, b=3, c=4)

        for i in range(10):
            self.mocked_method(1, 2, b=3, c=4)

        assert self.expectation.satisfied() is None

        # extra call should fail
        self.mocked_method(1, 2, b=3, c=4)
        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_error_on_multiple_call_expectation_due_to_missing_arg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=4)
        self.mocked_method(4, b=2, c=1)

        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_error_on_multiple_call_expectation_due_to_extra_arg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(100, 1, 2, b=3, c=4)
        self.mocked_method(4, 3, b=2, c=1)

        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_error_on_multiple_call_expectation_due_to_incorrect_arg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=4)
        self.mocked_method(50, 3, b=2, c=1)

        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_error_on_multiple_call_expectation_due_to_missing_kwarg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3)
        self.mocked_method(4, 3, b=2, c=1)

        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_error_on_multiple_call_expectation_due_to_incorrect_kwarg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=1000)
        self.mocked_method(4, 3, b=2, c=1)

        with pytest.raises(AssertionError):
            self.expectation.satisfied()

    def test_error_on_multiple_call_expectation_due_to_extra_kwarg(self):
        self.expectation.new_call_params(1, 2, b=3, c=4)
        self.expectation.new_call_params(4, 3, b=2, c=1)

        self.mocked_method(1, 2, b=3, c=4)
        self.mocked_method(4, 3, b=2, c=1, f=10)

        with pytest.raises(AssertionError):
            self.expectation.satisfied()


class NoCallsExpectationTests(TestCase):

    def setUp(self):
        self.mocked_method = Mock()
        self.expectation = NoCallsExpectation(self.mocked_method)

    def test_successful_no_calls_expectation(self):
        assert self.expectation.satisfied() is None

    def test_no_calls_expectation_fails_if_any_call(self):
        self.mocked_method(1, 2, b=3, c=4)
        with pytest.raises(AssertionError):
            assert self.expectation.satisfied() is None
