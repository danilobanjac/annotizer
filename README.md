# annotizer
# The fastest Python 3 Serializer

A serializer which leverages type annotations, allowing users to serialize their objects in a very practical and fast way.

## Documentation with examples for the `Serializer` class

The Serializer's `__init__` method accepts the following parameters:
- data    - Is either a single object or a list of objects
- fields  - You can serialize only certain fields 
            by providing them as a list
- many    - When multiple objects are being passed to the `data` parameter,
            set `many=True`
- to_json - In order to get json string as an output, pass `to_json=True`
            to the class initializer (as in the example below you could also
            pass other keyword parameters such as `skipkeys` in order to 
            customize the `dumps` function from the `json` module)

```Python
Serializer(data=data, many=True, to_json=True, allow_nan=False, skipkeys=True)
```

### Usage
```Python
from serializer import Serializer, make_serializer
```
| Field | Callable | New Alias | Description |
| ----- | -------- | --------- | ----------- |
|   a   |    ...   | 'new_alias_a' | 'a' is the Field that is going to be serialized. When Ellipsis object is provided as Callable, unmodified attribute value will be retrieved from the object. 'new_alias_a' is the New Alias for the field 'a'|
|       |  int, str, lambda num: num + 10  |               | Supply any other single argument function in order to run it after the value is retrieved from the object |
```Python
class ObjSerializer(Serializer):
    a: ... = 'new_alias_a'
    b: int = 'new_alias_b'
    c: str
    d: lambda num: num + 10
```
| Field | Callable | New Alias | Description |
| ----- | -------- | --------- | ----------- |
| e__nested_attribute | ... | 'attribute_of_nested_object' | With a double underscore syntax, the nested field can be accessed. For example: 'e' is another object that has attribute 'nested_attribute', access that attribute by using double underscore syntax '__' or 'accessor'. Using this feature, nested objects could be serialized as well (example below). Feature can be disabled by providing the attribute `disable_accessor` to the `Settings` class (example below) |
```Python
class ObjSerializer(Serializer):
    e__nested_attribute: ... = 'attribute_of_nested_object'
```
| Field | Callable | New Alias | Description |
| ----- | -------- | --------- | ----------- |
| f | NestedObjSerializer | | 'f' is an attribute that contains another object that is going to be serialized. `NestedObjSerializer` does not need to be instantiated but in order to provide additional parameters simply instantiate the serializer class normally. For example: `NestedObjSerializer(many=True)` |
| g__nested_object | NestedObjSerializer | | With 'accessor' feature, nested objects could be serialized as well
```Python
class NestedObjSerializer(Serializer):
    a: ...
    b: str
    c: float

class ObjSerializer(Serializer):
    f: NestedObjSerializer
    g__nested_object: NestedObjSerializer
```
| Field | Callable | New Alias | Description |
| ----- | -------- | --------- | ----------- |
| h | lambda x: x(*args, **kwargs) | | You can call any method of the object using this syntax as well. This would return the method `h` from the object and run it with the required `args` and `kwargs` |
```Python
class ObjSerializer(Serializer):
    h: lambda x: x(*args, **kwargs)
```
| Field | Callable | New Alias | Description |
| ----- | -------- | --------- | ----------- |
| i | 'get_i' | | When a string is supplied as Callable, new getter will be used, function with the name 'get_i' needs to be defined inside the class body |
```Python
class ObjSerializer(Serializer):
    i: 'get_i'

    def get_i(self, obj): 
        return obj.a + 20
```
### Adding Serializer Settings
| Attribute | Value | Description |
| ----- | -------- | --------- |
| optional | ('a', 'b', 'c', ) | Add an attribute called `optional` in order not to raise `AttributeError` when the attribute is not present on the object. The value for the `optional needs to be an iterable e.g. list, tuple, set, etc.|
| disable_accessor | ('d__nested_attribute', ) | Disable `accessor` feature by providing an iterable that contains field names for which this feature should be disabled |
```Python
class ObjSerializer(Serializer):
    a: ...
    b: ...
    c: ...
    d__nested_attribute: ...

    class Settings:
        optional = ('a', 'b', 'c', )
        disable_accessor = ('d__nested_attribute', )
```

## Documentation with examples for the `make_serializer` function

This function is provided in order to enable the user to dynamically
create new instances of the Serializer class.

`make_serializer function accepts the following parameters:
- name        - Name that will be given to the serializer class
- bases       - Classes that will be used as bases for the serializer class.
                For example: `bases=(Serializer, MixinClass)`
- fields      - Serializer fields, they are passed in the same manner as used on class.
                For example: `fields={'a': ..., 'b': str}`
- namespace   - Namespace is the class body. You can add field aliases, methods etc.
                For example: `namespace={'a': 'new_alias_a'}`

Additional keyword arguments could be passed, those arguments will be used
as a namespace for the `Settings` class (example below).

### Usage
```Python
from serializer import Serializer, make_serializer

new_serializer = make_serializer(
    name='NewSerializer',
    bases=(Serializer,),
    fields={'a': ..., 'b': str, 'c': int},
    namespace={'a': 'new_alias_a'},
    # Additional keyword arguments for the body of the 'Settings' class
    optional=('a',)
)
```
Everything above is equivalent to the following:
````Python
class NewSerializer(Serializer):
        a: ... = 'new_alias_a'
        b: str
        c: int
        
        class Settings:
            optional = ('a',)
```` 