from abc import ABCMeta, abstractmethod



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
