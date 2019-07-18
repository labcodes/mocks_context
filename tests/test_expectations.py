import pytest
from unittest import TestCase
from unittest.mock import Mock

from mocks_context.expectations import SingleCallExpectation


class SingleCallExpectationTests(TestCase):

    def setUp(self):
        self.mocked_method = Mock()
        self.expectation = SingleCallExpectation(self.mocked_method, 1, 2, b=3, c=4)

    def test_successful_single_call_expectation(self):
        self.mocked_method(1, 2, b=3, c=4)
        self.expectation.satisfied()  # shouldn't raise exception

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
