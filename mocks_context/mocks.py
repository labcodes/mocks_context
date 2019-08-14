from abc import ABCMeta, abstractmethod
from unittest.mock import patch

from mocks_context.expectations import SingleCallExpectation, MultipleCallsExpectation, NoCallsExpectation


class MockWithExpectation:
    """
    This class depends on a regular Python mock from mock lib and exposes
    a more semantic API to configure the behavior and expectations on it.
    """

    def __init__(self, mock):
        self.mock = mock
        self.expectation = None

    def set_output(self, should_return):
        """
        Defines what the mock will return
        """
        self.mock.return_value = should_return
        return self

    def set_many_outputs(self, should_return_per_call):
        """
        Defines what the mock will return per call.

        set_many_outputs have to be an iterable and each of its elements
        sets one of the return values
        """
        self.mock.side_effect = should_return_per_call
        return self

    def expect_single_call(self, *args, **kwargs):
        """
        Expects that the mock will be called only one time with *args and **kwargs
        """
        self.expectation = SingleCallExpectation(self.mock, *args, **kwargs)
        return self

    def expect_call(self, *args, **kwargs):
        """
        Expects that the mock will be called at least once with *args and **kwargs
        """
        if not isinstance(self.expectation, MultipleCallsExpectation):
            self.expectation = MultipleCallsExpectation(self.mock)

        self.expectation.new_call_params(*args, **kwargs)
        return self

    def expect_match_call_count(self, count=None):
        """
        Expects that the mock will be called count times.
        If count is None, the number of expected calls will be used
        """
        if not isinstance(self.expectation, MultipleCallsExpectation):
            self.expectation = MultipleCallsExpectation(self.mock)

        self.expectation.ensure_call_count(count)
        return self

    def expect_no_calls(self):
        """
        Expects that the mock will never be called.
        """
        self.expectation = NoCallsExpectation(self.mock)
        return self


class ContextualizedMockInterface(metaclass=ABCMeta):
    """
    This base class defines the required API exposed by mocks created via MocksContext
    """

    @abstractmethod
    def all_expectations(self):
        pass

    @abstractmethod
    def release(self):
        pass


class MockedFunction(ContextualizedMockInterface):
    """
    This class is used to mock regular python functions
    """

    def __init__(self, callable_path):
        """
        callable_path is a string with the full path to the function that'll be mocked.
        """
        self.patcher = patch(callable_path, spec=True)
        self._mock_function = self.patcher.start()
        self.mock_with_expectation = MockWithExpectation(self._mock_function)

    def all_expectations(self):
        """
        Returns all of the mocked function expectations
        """
        expec = self.mock_with_expectation.expectation
        if expec:
            return [expec]
        return []

    def release(self):
        self.patcher.stop()

    def set_output(self, *args, **kwargs):
        self.mock_with_expectation.set_output(*args, **kwargs)
        return self.mock_with_expectation

    def set_many_outputs(self, *args, **kwargs):
        self.mock_with_expectation.set_many_outputs(*args, **kwargs)
        return self.mock_with_expectation

    def expect_single_call(self, *args, **kwargs):
        self.mock_with_expectation.expect_single_call(*args, **kwargs)
        return self.mock_with_expectation

    def expect_call(self, *args, **kwargs):
        self.mock_with_expectation.expect_call(*args, **kwargs)
        return self.mock_with_expectation

    def expect_match_call_count(self, *args, **kwargs):
        self.mock_with_expectation.expect_match_call_count(*args, **kwargs)
        return self.mock_with_expectation

    def expect_no_calls(self, *args, **kwargs):
        self.mock_with_expectation.expect_no_calls(*args, **kwargs)
        return self.mock_with_expectation
