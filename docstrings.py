"""Contains documentation strings."""


SERIALIZER = """
Documentation with examples for the Serializer class.

Serializer __init__ accepts the following parameters:
    data    - Is either single object or list of objects
    fields  - You can serialize only certain fields 
              by providing list of those fields
    many    - When multiple objects are being passed to the 'data' parameter
              set 'many' to 'True'
    to_json - In order to get json string as output, pass 'to_json=True'
              to the class initializer. (Other keyword parameters can be passed
              as well in order to customize 'dumps' function from the 'json' module)
              For example: Serializer(data=data, many=True, to_json=True, 
                                      allow_nan=False, skipkeys=True)
Usage:
    from serializer import Serializer

    ### [SKIP] This class is a part of the examples from below.
    class NestedObjSerializer(Serializer):
        a: ...
        b: str
        c: float

    class ObjSerializer(Serializer):
    
        + -------------------------- Field that is going to be serialized.
        |   +----------------------- Ellipsis object has the special meaning, 
        |   |                        don't cast the value after is retrieved from the object.
        |   |          +------------ Provide the new alias for the field 'a'.
        |   |          |
        V   v          v
        a: ... = 'new_alias_a'
            +----------------------- Supply any other single argument function 
            |                        in order to run it after the value is retrieved
            |                        from the object.
            |
            v
        b: int = 'new_alias_b'
        c: str
                +------------------- Another example on how this feature can be used
                |                    by supplying the lambda function.
                |
                v
        d: lambda num: num + 10
         
         +-------------------------- With double underscore syntax, nested field can be accessed.
         |                           For example: 'e' is another object that has attribute 'nested_attribute',
         |                           access that attribute by using double underscore syntax '__' or 'accessor'.
         |                           Using this feature, nested objects could be serialized as well,
         |                           as you will see below. Feature can be disabled by
         |                           providing the attribute 'disable_accessor' to the 'Settings' class.
         |                           Example for this is provided below.
         v                           
        e__nested_attribute: ... = 'attribute_of_nested_object'
        
        +--------------------------- 'f' is an attribute that contains another object
        |                            that is going to be serialized. 
        |                             
        |           +--------------- 'NestedObjSerializer' does not need to be instantiated
        |           |                but in order to provide additional parameters 
        |           |                simply instantiate the serializer instance normally.
        v           v                For example: 'NestedObjSerializer(to_json=True)'.
        f: NestedObjSerializer
         
         +-------------------------- With 'accessor' feature nested objects could be serialized as well.
         |
         |
         v
        g__nested_object: NestedObjSerializer
        
                +------------------- You can as well call any callable of the object using this syntax.
                |                    This would call the method 'h' and provide required 'args' and 'kwargs'.
                |
                v  
        h: lambda x: x(*args, **kwargs)

              +--------------------- When string is supplied, new getter will be used,
              |                      function with the name 'get_i' needs to 
              |                      be defined inside the class body.
              |                                            __________
              |                                                 |
              v                                                 |
        i: 'get_i'                                              |
                                                                |  
              +-------------------------------------------------+
              |
              V
        def get_i(self, obj): 
            return obj.a + 20  # Just an example
        
                 +------------------ Add class 'Settings' to the class body,
                 |                   in order to control/add additional settings.
                 |
                 |           +------ Add attribute called 'optional' in order not to raise 
                 |           |       'AttributeError' when attribute is not present on the object.
                 v           |       Value for the 'optional' attribute needs to be an iterable. 
        class Settings:      |       For example: list, tuple, set, etc.
               +-------------+        
               |
               v           
            optional = (         +-- Disable 'accessor' feature by providing an iterable that contains
                'a', 'b', 'c'    |   field names for which this feature should be disabled.
            )                    |
                   +-------------+
                   |    
                   V
            disable_accessor = (
                'g__nested_object'
            )
        
        ### [COMBINING SERIALIZERS] Combine Serializers including Mixin classes by using class inheritance

        class FirstSer(Serializer):
            a: str
            b: int
            c: ...

        class DFieldMixin:
            d: ...

        class FinalSerializer(FirstSer, DFieldMixin):
            ...
"""

MAKE_SERIALIZER = """
Documentation with examples for the make_serializer function.

This function is provided in order to enable the user to dynamically
create new instances of the Serializer class.

'make_serializer' function accepts the following parameters:
    name      - Name that will be given to the serializer class
    bases     - Classes that will be used as bases for the serializer class.
                For example: 'bases=(Serializer, MixinClass)'
    fields    - Serializer fields, they are passed in the same manner as used on class.
                For example: 'fields={'a': ..., 'b': str}'
    namespace - Namespace is the class body. You can add field aliases, methods etc.
                For example: 'namespace={'a': 'new_alias_a'}'
    
    Additional keyword arguments could be passed, those arguments will be used
    as namespace for the 'Settings' class. See example below.
    
Usage:
    from serializer import Serializer, make_serializer
    
    new_serializer = make_serializer(
        name='NewSerializer',
        bases=(Serializer,),
        fields={'a': ..., 'b': str, 'c': int},
        namespace={'a': 'new_alias_a'},
        # Additional keyword arguments for the body of the 'Settings' class
        optional=('a',)
    )
    
    # Everything from the above is equivalent to the following:

    class NewSerializer(Serializer):
        a: ... = 'new_alias_a'
        b: str
        c: int
        
        class Settings:
            optional = ('a',)
"""
