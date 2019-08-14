from abc import ABCMeta, abstractmethod
from unittest.mock import Mock, patch, PropertyMock, call


class MocksContext:

    def __init__(self):
        self.mocks = []

    @property
    def expectations(self):
        return MocksExpectations(self.mocks)

    def mock_class(self, target, *args, **kwargs):
        kwargs['spec'] = target
        return self.mock(*args, **kwargs)

    def mock_method(self, method_name, imported_at):
        path = '.'.join([imported_at, method_name])
        new_mock = MockCallable(path)
        self.mocks.append(new_mock)
        return new_mock

    def mock_references(self, target):
        new_mock = MockReferences(target)
        self.mocks.append(new_mock)
        return new_mock

    def mock(self, *args, **kwargs):
        new_mock = MockClass(*args, **kwargs)
        self.mocks.append(new_mock)
        return new_mock

    def expectations_are_satisfied(self):
        self.expectations.satisfied()


class BaseMockWithExpectations(metaclass=ABCMeta):

    @abstractmethod
    def set_output(self, *args, **kwargs):
        pass

    @abstractmethod
    def set_many_outputs(self, *args, **kwargs):
        pass

    @abstractmethod
    def satisfies_expectations(self):
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


class MockClass(BaseMockWithExpectations, Mock):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mocks_expectations = {}
        self._propeties_mocks = {}
        self._methods_mocks = {}

    def set_output(self, method_name=None, will_return=None, as_property=False):
        mocked_method = self._get_or_create_mock(method_name, as_property)
        mocked_method.return_value =  will_return

        self._refresh_expectations(method_name, mocked_method)
        return self

    def set_many_outputs(self, method_name=None, will_return=None):
        mocked_method = self._get_or_create_mock(method_name)
        mocked_method.side_effect = will_return

        self._refresh_expectations(method_name, mocked_method)
        return self

    def satisfies_expectations(self):
        for expectation in self._mocks_expectations.values():
            expectation.satisfied()

    def expect_single_call(self, method_name=None, *args, **kwargs):
        mocked_method = self._get_or_create_mock(method_name, as_property=method_name in self._propeties_mocks)
        expectation = SingleCallExpectation(mocked_method, *args, **kwargs)
        self._mocks_expectations[method_name] = expectation
        return self

    def expect_call(self, method_name=None, *args, **kwargs):
        mocked_method = self._get_or_create_mock(method_name, as_property=method_name in self._propeties_mocks)
        expectation = self._mocks_expectations.get(method_name, MultipleCallsExpectation(mocked_method))
        expectation.new_call_params(*args, **kwargs)
        self._mocks_expectations[method_name] = expectation
        return self

    def expect_match_call_count(self, method_name=None, count=0):
        mocked_method = self._get_or_create_mock(method_name, as_property=method_name in self._propeties_mocks)
        expectation = self._mocks_expectations.get(method_name, MultipleCallsExpectation(mocked_method))
        expectation.count = count
        self._mocks_expectations[method_name] = expectation
        return self

    def expect_no_calls(self, method_name=None):
        mocked_method = self._get_or_create_mock(method_name, as_property=method_name in self._propeties_mocks)
        self._mocks_expectations[method_name] = NoCallsExpectation(mocked_method)
        return self

    def release(self):
        pass

    def _refresh_expectations(self, method_name, mocked_method):
        method_name = method_name or '__call__'
        if method_name in self._mocks_expectations:
            self._mocks_expectations[method_name].mocked_method = mocked_method

    def _get_or_create_mock(self, method_name, as_property=False):
        method_name = method_name or '__call__'

        if as_property:
            if method_name in self._methods_mocks:
                self._methods_mocks.pop(method_name)

            mock = self._propeties_mocks.get(method_name)
            if not mock:
                mock = PropertyMock()

            setattr(type(self), method_name, mock)
            self._propeties_mocks[method_name] = mock
        else:
            if method_name in self._propeties_mocks:
                self._propeties_mocks.pop(method_name)

            mock = self._methods_mocks.get(method_name)

            if not mock and not method_name == '__call__':
                mock = Mock()
                setattr(self, method_name, mock)
            elif not mock:
                mock = self

            self._methods_mocks[method_name] = mock

        return mock


class MockCallable(BaseMockWithExpectations):

    def __init__(self, callable_path):
        self.patcher = patch(callable_path, spec=True)
        self.mock = self.patcher.start()
        self.callble = callable
        self._expectation = None

    def set_output(self, will_return):
        self.mock.return_value = will_return
        return self

    def set_many_outputs(self, will_return):
        self.mock.side_effect = will_return
        return self

    def satisfies_expectations(self):
        if self._expectation:
            self._expectation.satisfied()

    def expect_single_call(self, *args, **kwargs):
        self._expectation = SingleCallExpectation(self.mock, *args, **kwargs)
        return self

    def expect_call(self, *args, **kwargs):
        if not isinstance(self._expectation, MultipleCallsExpectation):
            self._expectation = MultipleCallsExpectation(self.mock)

        self._expectation.new_call_params(*args, **kwargs)
        return self

    def expect_match_call_count(self, count):
        if not isinstance(self._expectation, MultipleCallsExpectation):
            self._expectation = MultipleCallsExpectation(self.mock)

        self._expectation.count = count
        return self

    def expect_no_calls(self, *args, **kwargs):
        raise NotImplementedError

    def release(self):
        self.patcher.stop()


class MockReferences(BaseMockWithExpectations):

    def __init__(self, target):
        self.target = target
        self.patchers = []
        self._mocks_expectations = {}
        self._propeties_mocks = {}
        self._methods_mocks = {}

    def set_output(self, method_name, will_return=None, as_property=False):
        mocked_method = self._get_or_create_mock(method_name, as_property)
        mocked_method.return_value = will_return

        self._refresh_expectations(method_name, mocked_method)
        return self

    def set_many_outputs(self, method_name, will_return=None):
        mocked_method = self._get_or_create_mock(method_name)
        mocked_method.side_effect = will_return

        self._refresh_expectations(method_name, mocked_method)
        return self

    def satisfies_expectations(self):
        for expectation in self._mocks_expectations.values():
            expectation.satisfied()

    def expect_single_call(self, method_name, *args, **kwargs):
        mocked_method = self._get_or_create_mock(method_name, as_property=method_name in self._propeties_mocks)
        expectation = SingleCallExpectation(mocked_method, *args, **kwargs)
        self._mocks_expectations[method_name] = expectation
        return self

    def expect_call(self, method_name, *args, **kwargs):
        mocked_method = self._get_or_create_mock(method_name, as_property=method_name in self._propeties_mocks)
        expectation = self._mocks_expectations.get(method_name, MultipleCallsExpectation(mocked_method))
        expectation.new_call_params(*args, **kwargs)
        self._mocks_expectations[method_name] = expectation
        return self

    def expect_match_call_count(self, method_name, count):
        mocked_method = self._get_or_create_mock(method_name, as_property=method_name in self._propeties_mocks)
        expectation = self._mocks_expectations.get(method_name, MultipleCallsExpectation(mocked_method))
        expectation.count = count
        self._mocks_expectations[method_name] = expectation
        return self

    def expect_no_calls(self, *args, **kwargs):
        raise NotImplementedError

    def release(self):
        for patcher in self.patchers:
            patcher.stop()

    def _refresh_expectations(self, method_name, mocked_method):
        if method_name in self._mocks_expectations:
            self._mocks_expectations[method_name].mocked_method = mocked_method

    def _get_or_create_mock(self, method_name, as_property=False):
        if as_property:
            ### TODO Property mock object's properties
            pass
        else:
            if method_name in self._propeties_mocks:
                self._propeties_mocks.pop(method_name)

            mock = self._methods_mocks.get(method_name)
            if not mock:
                new_patcher = patch.object(self.target, method_name)
                mock = new_patcher.start()
                self.patchers.append(new_patcher)

            setattr(self, method_name, mock)
            self._methods_mocks[method_name] = mock

        return mock


class MocksExpectations:

    def __init__(self, mocks):
        self.mocks = mocks

    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        # TODO __exit__ have to check if there's no previous exception raised
        #ipdb> sys.exc_info()
        #(<class 'AttributeError'>, AttributeError("'TerminalPdb' object has no attribute 'do_sys'",), <traceback object at 0x7fe02f3e4688>)
        #import traceback
        #print(traceback.format_exc())
        self.satisfied()

    def release_mocks(self):
        for mock in self.mocks:
            mock.release()

    def satisfied(self):
        try:
            for mock in self.mocks:
                mock.satisfies_expectations()
        finally:
            self.release_mocks()


class MockExpectation(metaclass=ABCMeta):

    @abstractmethod
    def satisfied(self):
        pass


class SingleCallExpectation(MockExpectation):

    def __init__(self, mocked_method, *args, **kwargs):
        self.mocked_method = mocked_method
        self.call_args = args
        self.call_kwargs = kwargs

    def satisfied(self):
        self.mocked_method.assert_called_once_with(*self.call_args, **self.call_kwargs)


class MultipleCallsExpectation(MockExpectation):

    def __init__(self, mocked_method, any_order=False):
        self.mocked_method = mocked_method
        self.calls = []
        self.count = 0
        self.any_order = any_order

    def new_call_params(self, *args, **kwargs):
        self.calls.append(call(*args, **kwargs))

    def satisfied(self):
        match_call_count = self.mocked_method.call_count == self.count
        if self.count:
            actual_calls = self.mocked_method.call_count
            msg = f'Call count does not match for {self.mocked_method}: {actual_calls} calls from {self.count} expected.'
            assert match_call_count, msg

        self.mocked_method.assert_has_calls(self.calls, any_order=self.any_order)


class NoCallsExpectation(MockExpectation):

    def __init__(self, mocked_method):
        self.mocked_method = mocked_method

    def satisfied(self):
        assert self.mocked_method.called is False
