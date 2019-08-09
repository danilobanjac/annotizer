# annotizer
# The fastest Python 3 Serializer

A python serializer which leverages Python3 class annotations, allowing users to serialize their objects in a very practical and fast way.

## Documentation
### Documentation with examples for the Serializer class.

Serializer `__init__ accepts the following parameters:
- data    - Is either single object or list of objects
- fields  - You can serialize only certain fields 
            by providing a list of those fields
- many    - When multiple objects are being passed to the 'data' parameter
            set 'many' to 'True'
- to_json - In order to get json string as output, pass 'to_json=True'
            to the class initializer. (As in the example below 
            other keyword parameters such as 'skipkeys' can be passed
            as well in order to customize the 'dumps' function from the 'json' module)

`Serializer(data=data, many=True, to_json=True, allow_nan=False, skipkeys=True)`

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
| e__nested_attribute | ... | attribute_of_nested_object | With double underscore syntax, nested field can be accessed. For example: 'e' is another object that has attribute 'nested_attribute', access that attribute by using double underscore syntax '__' or 'accessor'. Using this feature, nested objects could be serialized as well, as you will see below. Feature can be disabled by providing the attribute 'disable_accessor' to the 'Settings' class. Example for this is provided below. |
```Python
class ObjSerializer(Serializer):
    e__nested_attribute: ... = 'attribute_of_nested_object'
```
| Field | Callable | New Alias | Description |
| ----- | -------- | --------- | ----------- |
| f | NestedObjSerializer | | 'f' is an attribute that contains another object that is going to be serialized. 'NestedObjSerializer' does not need to be instantiated but in order to provide additional parameters simply instantiate the serializer class normally. For example: 'NestedObjSerializer(many=True)'. |
| g__nested_object | NestedObjSerializer | | With 'accessor' feature, nested objects could be serialized as well.
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
| h | lambda x: x(*args, **kwargs) | | You can as well call any method of the object using this syntax. This would call the method 'h' and provide required 'args' and 'kwargs'. |
```Python
class ObjSerializer(Serializer):
    h: lambda x: x(*args, **kwargs)
```
| Field | Callable | New Alias | Description |
| ----- | -------- | --------- | ----------- |
| i | get_i | | When string is supplied, new getter will be used, function with the name 'get_i' needs to be defined inside the class body. |
```Python
class ObjSerializer(Serializer):
    i: 'get_i'

    def get_i(self, obj): 
        return obj.a + 20
```
### Adding Serializer Settings
| Attribute | Value | Description |
| ----- | -------- | --------- |
| optional | ('a', 'b', 'c', ) | Add attribute called 'optional' in order not to raise 'AttributeError' when attribute is not present on the object. Value for the 'optional' attribute needs to be an iterable e.g. list, tuple, set, etc.|
| disable_accessor | ('d__nested_attribute', ) | Disable 'accessor' feature by providing an iterable that contains field names for which this feature should be disabled.|
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
