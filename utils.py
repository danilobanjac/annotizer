"""This module contains the utility functions for the serializer package.

* AnnotationsChainMap - ChainMap that returns a ordered keys
* HasNoAttribute - Singleton class object
* construct_accessor - Function that is used to enable access to the nested fields
* coroutine - Function that primes the coroutine and returns the generator 'send' function
* apply_getters - Function that will apply all the methods
                  on the object that needs to be serialized
* apply_getters_many - Wrapper around the 'apply_getters' for multiple object serialization
* get_attr - Function that implements attribute getter using coroutine
"""

from typing import Union, Type, Any, Callable, Tuple, List, Generator, Dict
from types import FunctionType
from collections import ChainMap
from itertools import chain
from functools import wraps, partial


# ------------------------------------------------------------------------------------- #
# TYPE HINTS

FieldAlias = str
Getter = Callable
Field = Tuple[FieldAlias, Getter, Union[Callable, None]]
GetterGeneratorFunc = Generator[Union[None, Dict], Type[object], None]
GetterManyGeneratorFunc = Generator[Union[None, List[Dict]], List[Type[object]], None]


class AnnotationsChainMap(ChainMap):
    """Chain map that is used specifically to
    chain the class annotations and keep their order."""

    def __iter__(self):
        # Overriding '__iter__' in order to
        # maintain the order of the unique keys
        return iter(dict.fromkeys(chain.from_iterable(self.maps)))


class HasNoAttribute:
    """Singleton class."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


def construct_accessor(attribute: str, accessor: str = "") -> str:
    """Given the attribute, construct appropriate accessor.

    Example:
        'a__b' -> 'a.b'
        'a__b__c' -> 'a.b.c'
        '_a___c' -> '_a._c'
        ...
    """

    def valid(string: str) -> Union[str, bool]:
        """Validate that string does not contain only underscores."""

        return string and not string == len(string) * "_"

    before, dunder, after = attribute.partition("__")

    if valid(before) and valid(after):
        accessor += before + "."
        return construct_accessor(after, accessor)

    accessor += before + dunder

    if valid(after):
        return construct_accessor(after, accessor)

    return accessor + after


def coroutine(func: Callable) -> Callable:
    """Decorator that primes the coroutine
    and returns the generator 'send' function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        gen_func = func(*args, **kwargs)
        next(gen_func)
        return gen_func.send

    return wrapper


@coroutine
def apply_getters(fields: List[Field]) -> Union[Callable, GetterGeneratorFunc]:
    """Apply the getter methods on the passed object."""

    # Setup phase
    has_no_attribute = HasNoAttribute()

    # Main phase
    object_ = yield

    while True:
        ser = {}
        for field_alias, getter, callable_ in fields:
            value = getter(object_)
            if value is has_no_attribute:
                continue
            if callable_ is None:
                ser[field_alias] = value
            else:
                ser[field_alias] = callable_(value)
        object_ = yield ser


@coroutine
def apply_getters_many(fields: List[Field]) -> Union[Callable, GetterManyGeneratorFunc]:
    """Wrapper around 'apply_getters' function to
    allow serialisation of multiple objects."""

    # Setup phase
    getter = apply_getters(fields)

    # Main phase
    objects = yield

    while True:
        objects = yield [getter(obj) for obj in objects]


@coroutine
def get_attr(attributes: str) -> Union[Any, HasNoAttribute]:
    """Get attribute function that works as coroutine."""

    # Setup phase
    getattr_ = getattr
    has_no_attribute = HasNoAttribute()
    names = attributes.split(".")

    # Main phase
    obj = yield

    if len(names) == 1:
        attr, = names
        while True:
            obj = yield getattr_(obj, attr, has_no_attribute)
    else:
        while True:
            for attr in names:
                obj = getattr_(obj, attr, has_no_attribute)
            obj = yield obj


def add_docstring(
    obj: Union[FunctionType, Type[object]] = None, doc: str = None
) -> Callable:
    """Attach the documentation string to the object."""

    if obj is None:
        return partial(add_docstring, doc=doc)
    obj.__doc__ = doc

    return obj
