import typing

from validation.validators import construct_error


class Schema:

    def __new__(cls, **kwargs):
        """
        Collects mandatory fields into a list and binds it to the class.
        Only has to run once for every class, hence the `_processed` property.
        """
        if not hasattr(cls, '_processed'):
            mandatory_fields = []
            for k in cls.__annotations__.keys():

                # collect mandatory fields
                if not hasattr(cls, k):
                    mandatory_fields.append(k)

                # reassign variables to private variables
                setattr(cls, k, None)

            cls._mandatory_fields = mandatory_fields
            cls._processed = True

        return super(Schema, cls).__new__(cls)

    def __init__(self, **kwargs):
        mandatory_fields = self._mandatory_fields.copy()

        class_items = self.__class__.__dict__
        self._validation_errors = []
        # set attributes
        for k, v in kwargs.items():
            self._check_unknown_attributes(k)

            # check if type matches the annotated type
            self._validate_type(k, v)

            # remove provided attributes from the mandatory list
            # this is necessary to accept provided `None` values as well
            if k in mandatory_fields and v is not None:
                mandatory_fields.remove(k)

            # run validations
            validation_field = 'validate_%s' % k
            if validation_field in class_items:
                v = class_items[validation_field](self, v)

            setattr(self, k, v)

        # check if all mandatory fields have been set
        self._check_mandatory_fields(mandatory_fields)

    def _check_unknown_attributes(self, attr_name):
        """
        Checks for unknown attributes.

        :param attr_name: the attribute's name
        """
        if not hasattr(self, attr_name):
            self._validation_errors.append(
                construct_error(attr_name, "unknown attribute"))

    def _validate_type(self, attr_name, attr_val):
        """
        Validates the type of the property based on the annotation.

        :param attr_name: the name of the attribute
        :param attr_val: the value of the attribute
        :return:
        """
        type_ = type(attr_val)
        annotated_type = self.__class__.__annotations__[attr_name]
        if attr_val is None:
            # if the value is None, it's type will be NoneType
            # we check for mandatory value assignment later
            pass
        elif type(annotated_type) is typing.GenericMeta and \
                issubclass(annotated_type, list):
            # check typing.List
            try:
                list_element_type = annotated_type.__args__[0]
                for elem in attr_val:
                    if not type(elem) is list_element_type:
                        self._validation_errors.append(
                            construct_error(
                                attr_name, "wrong type in list. expected: "
                                           "'%s', provided: '%s'"
                                           % (list_element_type, type(elem)))
                        )
                        break
            except (IndexError, TypeError):
                # if we get either of these exceptions it means that the
                # annotation is a generic List with no type hints for it's
                # content
                pass

        elif not type_ == annotated_type:
            self._validation_errors.append(
                construct_error(attr_name, "wrong type. expected: '%s',"
                                           "provided: '%s'"
                                % (annotated_type, type_)))

    def _check_mandatory_fields(self, mandatory_fields):
        for mandatory in mandatory_fields:
            if getattr(self, mandatory) is None:
                self._validation_errors.append(
                    construct_error(mandatory, "mandatory field not set"))

    def __repr__(self):
        return str(self.__dict__)
