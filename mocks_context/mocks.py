from abc import ABCMeta, abstractmethod
from unittest.mock import patch

from mocks_context.expectations import SingleCallExpectation, MultipleCallsExpectation, NoCallsExpectation


class MockWithExpectationsInterface(metaclass=ABCMeta):
    """
    This base class defines the required API exposed by mocks created via MocksContext
    """

    @abstractmethod
    def set_output(self, *args, **kwargs):
        pass

    @abstractmethod
    def set_many_outputs(self, *args, **kwargs):
        pass

    @abstractmethod
    def all_expectations(self):
        pass

    @abstractmethod
    def expect_single_call(self, *args, **kwargs):
        pass

    @abstractmethod
    def expect_call(self, *args, **kwargs):
        pass

    @abstractmethod
    def expect_match_call_count(self, *args, **kwargs):
        pass

    @abstractmethod
    def expect_no_calls(self, *args, **kwargs):
        pass

    @abstractmethod
    def release(self):
        pass


class MockedFunction(MockWithExpectationsInterface):
    """
    This class is used to mock regular python functions
    """

    def __init__(self, callable_path):
        """
        callable_path is a string with the full path to the function that'll be mocked.
        """
        self.patcher = patch(callable_path, spec=True)
        self.mock = self.patcher.start()
        self._expectation = None

    def set_output(self, should_return):
        """
        Defines what the mocked function will return
        """
        self.mock.return_value = should_return
        return self

    def set_many_outputs(self, should_return_per_call):
        """
        Defines what the mocked function will return per function call.

        should_return_per_call have to be an iterable and each of its elements
        sets one of the return values
        """
        self.mock.side_effect = should_return_per_call
        return self

    def all_expectations(self):
        """
        Returns all of the mocked function expectations
        """
        return [self._expectation]

    def expect_single_call(self, *args, **kwargs):
        """
        Expects that the function will be called only one time with *args and **kwargs
        """
        self._expectation = SingleCallExpectation(self.mock, *args, **kwargs)
        return self

    def expect_call(self, *args, **kwargs):
        """
        Expects that the function will be called at least once with *args and **kwargs
        """
        if not isinstance(self._expectation, MultipleCallsExpectation):
            self._expectation = MultipleCallsExpectation(self.mock)

        self._expectation.new_call_params(*args, **kwargs)
        return self

    def expect_match_call_count(self, count=None):
        """
        Expects that the function will be called count times.
        If count is None, the number of expected calls will be used
        """
        if not isinstance(self._expectation, MultipleCallsExpectation):
            self._expectation = MultipleCallsExpectation(self.mock)

        self._expectation.ensure_call_count(count)
        return self

    def expect_no_calls(self):
        """
        Expects that the function will never be called.
        """
        self._expectation = NoCallsExpectation(self.mock)
        return self

    def release(self):
        self.patcher.stop()
