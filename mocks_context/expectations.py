from abc import ABCMeta, abstractmethod


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
