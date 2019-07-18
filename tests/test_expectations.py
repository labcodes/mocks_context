import pytest
from unittest import TestCase
from unittest.mock import Mock

from mocks_context.expectations import SingleCallExpectation, MultipleCallsExpectation, NoCallsExpectation, ExpectationInterface, MocksExpectationsManager
from mocks_context.mocks import MockWithExpectations


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


class MocksExpectationsManagerTests(TestCase):

    def setUp(self):
        self.mock_1 = Mock(spec=MockWithExpectations)
        self.mock_2 = Mock(spec=MockWithExpectations)
        self.expectations = MocksExpectationsManager([self.mock_1, self.mock_2])

    def test_successful_mocks_expectations(self):
        expectations_1 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        expectations_2 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        self.mock_1.all_expectations.return_value = expectations_1
        self.mock_2.all_expectations.return_value = expectations_2
        for expec in expectations_1 + expectations_2:
            expec.satisfied.return_value = None

        assert self.expectations.satisfied() is None

        # ensure it queries over all expecations
        self.mock_1.all_expectations.assert_called_once_with()
        self.mock_2.all_expectations.assert_called_once_with()
        # ensure it checks if all expectations are satisfied
        for expec in expectations_1 + expectations_2:
            expec.satisfied.assert_called_once_with()
        # make sure it releases the mocks from their patches
        self.mock_1.release.assert_called_once_with()
        self.mock_2.release.assert_called_once_with()

    def test_successful_mocks_expectations_without_releasing_mock(self):
        expectations_1 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        expectations_2 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        self.mock_1.all_expectations.return_value = expectations_1
        self.mock_2.all_expectations.return_value = expectations_2
        for expec in expectations_1 + expectations_2:
            expec.satisfied.return_value = None

        assert self.expectations.satisfied(release_mocks=False) is None

        # ensure it queries over all expecations
        self.mock_1.all_expectations.assert_called_once_with()
        self.mock_2.all_expectations.assert_called_once_with()
        # ensure it checks if all expectations are satisfied
        for expec in expectations_1 + expectations_2:
            expec.satisfied.assert_called_once_with()
        # make sure it does not release the mocks from their patches
        assert self.mock_1.release.called is False
        assert self.mock_2.release.called is False

    def test_release_mocks_if_any_assertion_error(self):
        expectations_1 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        expectations_2 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        self.mock_1.all_expectations.return_value = expectations_1
        self.mock_2.all_expectations.return_value = expectations_2
        for expec in expectations_1 + expectations_2:
            expec.satisfied.side_effect = AssertionError

        with pytest.raises(AssertionError):
            self.expectations.satisfied(release_mocks=False)

        # ensure it queries over all expecations
        self.mock_1.all_expectations.assert_called_once_with()
        self.mock_2.all_expectations.assert_called_once_with()

        # ensure it ignores further expectations after one fail
        expectations_1[0].satisfied.assert_called_once_with()
        for expec in expectations_1[1:] + expectations_2:
            assert expec.satisfied.called is False

        # make sure it releases the mocks from their patches
        self.mock_1.release.assert_called_once_with()
        self.mock_2.release.assert_called_once_with()

    def test_successful_mocks_expectations_as_context_manager(self):
        expectations_1 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        expectations_2 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        self.mock_1.all_expectations.return_value = expectations_1
        self.mock_2.all_expectations.return_value = expectations_2
        for expec in expectations_1 + expectations_2:
            expec.satisfied.return_value = None

        with self.expectations:
            assert True

        # ensure it queries over all expecations
        self.mock_1.all_expectations.assert_called_once_with()
        self.mock_2.all_expectations.assert_called_once_with()
        # ensure it checks if all expectations are satisfied
        for expec in expectations_1 + expectations_2:
            expec.satisfied.assert_called_once_with()
        # make sure it releases the mocks from their patches
        self.mock_1.release.assert_called_once_with()
        self.mock_2.release.assert_called_once_with()

    def test_release_mocks_if_any_assertion_error_as_context_manager(self):
        expectations_1 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        expectations_2 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        self.mock_1.all_expectations.return_value = expectations_1
        self.mock_2.all_expectations.return_value = expectations_2
        for expec in expectations_1 + expectations_2:
            expec.satisfied.side_effect = AssertionError

        with pytest.raises(AssertionError):
            with self.expectations:
                pass

        # ensure it queries over all expecations
        self.mock_1.all_expectations.assert_called_once_with()
        self.mock_2.all_expectations.assert_called_once_with()

        # ensure it ignores further expectations after one fail
        expectations_1[0].satisfied.assert_called_once_with()
        for expec in expectations_1[1:] + expectations_2:
            assert expec.satisfied.called is False

        # make sure it releases the mocks from their patches
        self.mock_1.release.assert_called_once_with()
        self.mock_2.release.assert_called_once_with()

    def test_do_not_check_for_expectations_if_any_error_was_raised_inside_the_context_manager(self):
        def foo():
            raise KeyError('Sample of an exception')

        expectations_1 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        expectations_2 = [
            Mock(spec=ExpectationInterface),
            Mock(spec=ExpectationInterface),
        ]
        self.mock_1.all_expectations.return_value = expectations_1
        self.mock_2.all_expectations.return_value = expectations_2

        with pytest.raises(KeyError):
            with self.expectations:
                foo()

        # ensure it queries over all expecations
        self.mock_1.all_expectations.called is False
        self.mock_2.all_expectations.called is False

        # ensure it ignores all expectations
        for expec in expectations_1 + expectations_2:
            assert expec.satisfied.called is False

        # make sure it releases the mocks from their patches
        self.mock_1.release.assert_called_once_with()
        self.mock_2.release.assert_called_once_with()


