import functools
import uuid

from validation import construct_error


def not_none(validation_field):
    """
    Checks whether a value is None
    """

    @functools.wraps(validation_field)
    def validator(self, value):
        prop_name = validation_field.__name__.split('_')[1]
        if value is None:
            self._validation_errors.append(
                construct_error(self.__class__.__name__,
                                prop_name,
                                'None value'))
        return validation_field(self, value)

    return validator


def not_empty(validation_field):
    """
    Checks whether a value is empty (which is either None or an empty value).
    """

    @functools.wraps(validation_field)
    def validator(self, value):
        prop_name = validation_field.__name__.split('_')[1]
        if not value and value is not 0:
            self._validation_errors.append(
                construct_error(self.__class__.__name__,
                                prop_name,
                                'empty value'))
        return validation_field(self, value)
    return validator


def min_size(size: int):
    """Checks whether the value has the minimum size (<)."""

    def decorator(validator_function):
        def validator(self, value):
            prop_name = validator_function.__name__.split('_')[1]
            if len(value) < size:
                self._validation_errors.append(
                    construct_error(self.__class__.__name__,
                                    prop_name,
                                    'minimum size %d not reached' % size))
            return validator_function(self, value)
        return validator
    return decorator


def max_size(size: int):
    """Checks whether the value has the maximum size (>)."""

    def decorator(validator_function):
        def validator(self, value):
            prop_name = validator_function.__name__.split('_')[1]
            if len(value) > size:
                self._validation_errors.append(
                    construct_error(self.__class__.__name__,
                                    prop_name,
                                    'maximum size %d exceeded' % size))
            return validator_function(self, value)
        return validator
    return decorator


def valid_uuid(validation_field):
    """
    Checks whether the value is a valid UUID.
    """

    @functools.wraps(validation_field)
    def validator(self, value):
        prop_name = validation_field.__name__.split('_')[1]
        try:
            uuid.UUID(value)
        except (ValueError, AttributeError):
            self._validation_errors.append(
                construct_error(self.__class__.__name__,
                                prop_name,
                                '{} is not a valid uuid'.format(value)))
        return validation_field(self, value)
    return validator