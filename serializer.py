"""Contains main logic for the Serializer package.

* Serializer - Main Serializer class
* make_serializer - Dynamically construct the Serializer class
"""

import keyword
from json import dumps
from operator import attrgetter
from itertools import chain
from collections import ChainMap

from typing import (
    Optional,
    Tuple,
    Union,
    Callable,
    Sequence,
    Type,
    ChainMap as ChainMap_,
    List,
    Dict,
    Any,
    Mapping,
)

from types import new_class

from .exceptions import SerializerError, MethodError, FieldError, FieldIdentifierError
from .utils import (
    AnnotationsChainMap,
    get_attr,
    construct_accessor,
    add_docstring,
    apply_getters,
)

from .docstrings import SERIALIZER, MAKE_SERIALIZER

__all__ = ["Serializer", "make_serializer"]


# ------------------------------------------------------------------------------------- #
# TYPE HINTS

GetterName = str
FieldAlias = str
Getter = Callable
MergedAnnotations = ChainMap_[str, Any]
MergedNamespaces = ChainMap_[str, Any]
Field = Tuple[FieldAlias, Getter, Union[Callable, None]]
ParsedFields = Dict[GetterName, Field]
SerializedData = Union[List[Dict], Dict, str, None]

# ------------------------------------------------------------------------------------- #
# CONSTANTS

ANNOTATIONS = "__annotations__"
NAMESPACE = "__dict__"
FIELDS = "_Serializer__fields"
WITHOUT_CALLABLE = None

# ------------------------------------------------------------------------------------- #
# SERIALIZER


@add_docstring(doc=SERIALIZER)
class Serializer:
    @classmethod
    def _merge_bases(
        cls: Type["Serializer"]
    ) -> Tuple[MergedAnnotations, MergedNamespaces]:
        """Merge annotations and namespaces of all base classes in the mro."""

        return (
            AnnotationsChainMap(
                *[
                    getattr(base, ANNOTATIONS, {})
                    for base in cls.mro()
                    if base is not object
                ]
            ),
            ChainMap(
                *[
                    getattr(base, NAMESPACE, {})
                    for base in cls.mro()
                    if base is not object
                ]
            ),
        )

    @classmethod
    def _construct_fields(
        cls: Type["Serializer"], fields: MergedAnnotations, namespace: MergedNamespaces
    ) -> ParsedFields:
        """Parse the merged annotations and construct the serializer fields."""

        parsed_fields = {}
        settings = namespace.get("Settings")
        optional_fields = getattr(settings, "optional", [])
        disable_accessor = getattr(settings, "disable_accessor", [])

        for field_name, callable_ in fields.items():
            # Field alias can be changed with this syntax
            # a: str = 'new_alias_a'
            # Because of that, check if value is present in the class body
            # if it is, used that as new alias, otherwise fallback to 'field_name'
            field_alias = namespace.get(field_name, field_name)

            if field_name in disable_accessor:
                getter_name = field_name
            else:
                getter_name = construct_accessor(field_name)

            if field_name in optional_fields:
                getter = get_attr(getter_name).send
            else:
                getter = attrgetter(getter_name)

            if callable_ is Ellipsis:
                callable_ = WITHOUT_CALLABLE
            elif isinstance(callable_, Serializer):
                callable_ = callable_.serialize
            elif isinstance(callable_, str):
                # Field getter can be changed with this syntax
                # a: 'getter_name' -> Where 'getter_name' is method in the class body
                try:
                    getter = namespace[callable_].__get__(cls)
                    callable_ = WITHOUT_CALLABLE
                except KeyError:
                    raise MethodError(
                        f"Missing '{callable_}' method in the serializer body"
                    )
                except AttributeError:
                    raise MethodError(
                        f"'{namespace[callable_]}' is not a valid getter method"
                    )
            elif not callable(callable_):
                raise FieldError(
                    f"Invalid callable for the field: {field_name}: {callable_}"
                )

            parsed_fields[field_name] = (field_alias, getter, callable_)

        return parsed_fields

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__fields = cls._construct_fields(*cls._merge_bases())

    def __new__(cls, *args, **kwargs):
        if cls is Serializer:
            raise SerializerError(
                "Initialising the Serializer class directly is not allowed"
            )
        return super().__new__(cls)

    def __init__(
        self,
        data=None,
        fields: Sequence[str] = None,
        many: Optional[bool] = False,
        to_json: Optional[bool] = False,
        **dumps_options,
    ):
        self.data = data
        self.many = many
        self.to_json = to_json
        self.dumps_options = dumps_options or {}
        self._serialized_data: SerializedData = None
        # Create a shallow-copy
        self._fields: List[Field] = list(self.get_fields.values())
        if fields is not None:
            unknown_fields = set(fields) - self.get_fields.keys()
            if unknown_fields:
                raise FieldError(
                    f"One or more unknown fields are being passed: "
                    f"{', '.join(unknown_fields)}"
                )
            self._fields = [
                field
                for getter_name, field in self.get_fields.items()
                if getter_name in fields
            ]

    @property
    def get_fields(self) -> ParsedFields:
        """Returns protected attribute '__fields'."""

        return getattr(self, FIELDS)

    def serialize(self, obj: Optional[Type[object]] = None) -> SerializedData:
        """Serialize either single object or list of the objects."""

        if self._serialized_data:
            return self._serialized_data

        data = self.data or obj

        gen_func = apply_getters(self._fields)
        apply_getters_ = gen_func.send

        if self.to_json:
            self._serialized_data = dumps(
                data, default=apply_getters_, **self.dumps_options
            )
        elif self.many:
            self._serialized_data = list(map(apply_getters_, data))
        else:
            self._serialized_data = apply_getters_(data)

        return self._serialized_data


@add_docstring(doc=MAKE_SERIALIZER)
def make_serializer(
    name: str,
    bases: Optional[Tuple[Type[object], ...]] = None,
    fields: Optional[Mapping[str, Any]] = None,
    namespace: Optional[Mapping[str, Any]] = None,
    **serializer_settings,
):

    bases = (Serializer,) if bases is None else bases
    fields = {} if fields is None else fields
    namespace = {} if namespace is None else namespace

    # Add Settings class to the namespace
    if serializer_settings:
        namespace.update(
            Settings=new_class(
                "Settings",
                bases=(object,),
                exec_body=lambda ns: ns.update(serializer_settings),
            )
        )

    for field_name in chain(fields, namespace):
        if not isinstance(field_name, str) or not field_name.isidentifier():
            raise FieldIdentifierError(
                f"Field names must be valid identifiers: {field_name!r}"
            )
        if keyword.iskeyword(field_name):
            raise FieldIdentifierError(
                f"Field names must not be python keywords: {field_name!r}"
            )

    if not any(issubclass(base, Serializer) for base in bases):
        raise SerializerError(
            "At least one base class needs to be the subclass of the 'Serializer'"
        )

    namespace[ANNOTATIONS] = fields

    return new_class(name=name, bases=bases, exec_body=lambda ns: ns.update(namespace))
