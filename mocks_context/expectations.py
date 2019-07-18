from abc import ABCMeta, abstractmethod
from unittest.mock import call


class ExpectationInterface(metaclass=ABCMeta):
    """
    Base class to define an Expectation interface
    """

    @abstractmethod
    def satisfied(self):
        """
        satisfied implementation should either pass silently or raise AssertionErrors
        the same way python's mock methods such as assert_called_once_with or assert_has_calls does
        """


class SingleCallExpectation(ExpectationInterface):
    """
    Ensures that a mocked method was called only one time with the specified args and kwargs.
    """

    def __init__(self, mocked_method, *args, **kwargs):
        self.mocked_method = mocked_method
        self.call_args = args
        self.call_kwargs = kwargs

    def satisfied(self):
        """
        Will raise exception if unmatching args or kwargs or if called more than one time.
        """
        self.mocked_method.assert_called_once_with(*self.call_args, **self.call_kwargs)


class MultipleCallsExpectation(ExpectationInterface):
    """
    Ensures that a mocked method has the specified calls respecting the expectations order by default.
    Exposed attributes:
    - any_order (default=False): if True ignores the calls order;
                                 if False, satisfied will raise an AssertionError if calls order differs
                                 from the expectations order
    - match_count (default=False: if True, will check the mock call count againts the number of expected calls
    - count (default=0): if not 0, will replace the number of expected calls in match count checking
    """

    def __init__(self, mocked_method, any_order=False, match_count=False):
        self.mocked_method = mocked_method
        self._calls = []
        self.count = 0
        self.any_order = any_order
        self.match_count = match_count

    def new_call_params(self, *args, **kwargs):
        """
        Will add the *args, **kwargs as an expected call in the expected calls list
        """
        self._calls.append(call(*args, **kwargs))

    def satisfied(self):
        if self.match_count:
            expected_count = self.count or len(self._calls)
            match_call_count = self.mocked_method.call_count == expected_count

            if not match_call_count:
                actual_calls = self.mocked_method.call_count
                msg = f'Call count does not match for {self.mocked_method}: {actual_calls} calls from {expected_count} expected.'
                assert match_call_count, msg

        self.mocked_method.assert_has_calls(self._calls, any_order=self.any_order)


class NoCallsExpectation(ExpectationInterface):
    """
    Ensures that a mocked method wasn't called at all
    """

    def __init__(self, mocked_method):
        self.mocked_method = mocked_method

    def satisfied(self):
        call_count = self.mocked_method.call_count
        calls = self.mocked_method.call_args_list
        msg = f'Mock {self.mocked_method} was called {call_count} times with the calls: {calls}.'
        assert self.mocked_method.called is False, msg
