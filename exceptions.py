"""This module contains all exception classes for the serializer package.

* SerializerError
* MethodError
* FieldError
* FieldIdentifierError
"""


class SerializerError(Exception):
    """Base serializer error."""


class MethodError(SerializerError):
    """Base method error."""


class FieldError(SerializerError):
    """All errors related to the serializer fields."""


class FieldIdentifierError(FieldError):
    """Invalid identifier for the field."""
