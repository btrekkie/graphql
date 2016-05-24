def graphql_object(object_name, description=None):
    """Annotate a class as a GraphQL type with the specified name.

    Decorator that annotates a class as a GraphQL concrete object type
    with the specified type name.  A class may not have multiple
    graphql_object annotations, but it may have both a graphql_object
    and a graphql_interface annotation.

    An object obj's concrete GraphQL type is given by the first element
    in inspect.getmro(obj.__class__) that has a graphql_object
    annotation.  Apart from scalars, lists, tuples, enum values, and the
    value None, all objects exposed through GraphQL must have a concrete
    GraphQL type.  It is possible for a base class and a derived class
    to both have graphql_object annotations.  In this case, as far as
    GraphQL queries are concerned, there is no relationship between the
    base and derived classes.

    basestring object_name - The type name.
    basestring description - A description of the type, or None.
        GraphQL favors the Markdown format.
    """
    def decorator(cls):
        cls._graphql_object_name = object_name
        cls._graphql_object_description = description
        return cls
    return decorator


def graphql_interface(interface_name, description=None):
    """Annotate a class as a GraphQL interface with the specified name.

    Decorator that annotates a class as a GraphQL interface with the
    specified type name.  At present, we do not support annotating a
    class with multiple graphql_interface annotations.

    There is one gotcha to be aware of when using graphql_interface.
    Apart from scalars, lists, tuples, enum values, and the value None,
    all objects exposed through GraphQL must have a concrete GraphQL
    type, indicated by a graphql_object annotation.  For example,
    suppose a Python class Character is annotated with
    graphql_interface('Character'), and it has a subclass called "Droid"
    that has no annotations.  Say there is a Python method
    Character.friends() that is declared to return a list of type
    Character, and this method returns a list containing a Droid.  Any
    attempt to access a character's friends using GraphQL would result
    in an error at runtime.  This is because Droid objects have no
    concrete GraphQL type, so we cannot expose them through GraphQL.  To
    fix this, we could add a graphql_object('Droid') annotation to the
    Droid class.

    basestring interface_name - The type name.
    basestring description - A description of the type, or None.
        GraphQL favors the Markdown format.
    """
    def decorator(cls):
        cls._graphql_interface_name = interface_name
        cls._graphql_interface_description = description
        return cls
    return decorator


def graphql_input_object(name, description=None):
    """Annotate a static method or function as an input object description.

    Decorator that annotates a static method or global function as
    returning a map defining a GraphQL input object type.  The function
    takes no arguments and returns a map from the names of the fields to
    their type strings.  In Python, we represent input objects as
    dictionaries.

    basestring name - The name of the input object type.
    basestring description - A description of the type, or None.
        GraphQL favors the Markdown format.
    """
    def decorator(func):
        func._graphql_input_object_name = name
        func._graphql_input_object_description = description
        return func
    return decorator


def graphql_union(name, description=None):
    """Annotate a static method or global function as a description of a union.

    Decorator that annotates a static method or global function as
    returning a list of the names of the types that comprise a GraphQL
    union type.  The types must be object, interface, and union types.
    At present, we do not support annotating a function with multiple
    graphql_union annotations.

    basestring name - The name of the union type.
    basestring description - A description of the type, or None.
        GraphQL favors the Markdown format.
    """
    def decorator(func):
        func._graphql_union_name = name
        func._graphql_union_description = description
        return func
    return decorator


def graphql_enum(enum_name, description=None):
    """Annotate a static method or global function as a description of an enum.

    Decorator that annotates a static method or global function as
    returning a map defining a GraphQL enum type.  The function takes no
    arguments and returns a map from the GraphQL constant name of each
    enum value to the Python object representation of the value.  It
    must be a one-to-one mapping whose values are hashable.  At present,
    we do not support annotating a function with multiple
    graphql_enum annotations.

    basestring enum_name - The name of the enum type.
    basestring description - A description of the type, or None.
        GraphQL favors the Markdown format.
    """
    def decorator(func):
        func._graphql_enum_name = enum_name
        func._graphql_enum_description = description
        return func
    return decorator


def graphql_scalar(scalar_name, description=None):
    """Annotate a GraphQlScalarDescriptor as a GraphQL scalar.

    Decorator that annotates a GraphQlScalarDescriptor subclass as a
    GraphQL scalar with the specified type name.  See
    GraphQlScalarDescriptor.  At present, we do not support annotating
    a class with multiple graphql_scalar annotations.

    basestring scalar_name - The type name.
    basestring description - A description of the type, or None.
        GraphQL favors the Markdown format.
    """
    def decorator(cls):
        cls._graphql_scalar_name = scalar_name
        cls._graphql_scalar_description = description
        return cls
    return decorator


def graphql_field(
        field_name, field_type, arguments={}, context_args=[],
        description=None, is_deprecated=False, deprecation_reason=None):
    """Decorator that annotates a method as corresponding to a GraphQL field.

    The field appears in the GraphQL types for any of the containing
    class's subclasses that are annotated with graphql_object or
    graphql_interface.  The value of the field for a particular object
    is equal to the method's return value.

    To be precise, we do not necessarily call the decorated method on a
    given object; rather, we call the method with the same name as the
    decorated method.  For example, if we decorate a method Foo.foo()
    using graphql_field, and Bar overrides foo(), then for an object of
    type Bar, we obtain the field's value by calling Bar's
    implementation of foo(), not Foo's implementation.  In other words,
    we respect ordinary method overriding semantics.

    At present, we do not support annotating a method with multiple
    graphql_field annotations.

    basestring field_name - The name of the field.
    basestring field_type - The GraphQL type of the field's value.
    dict<basestring, basestring> arguments - A map from the names of the
        arguments to the field in GraphQL to their GraphQL types.  We
        pass the arguments to the method as keyword arguments, after
        changing the arguments' names from camelCase to snake_case.  Any
        arguments whose values are not supplied are omitted from the
        keyword arguments.  As such, we will use any default values for
        such arguments defined in Python.
    list<basestring> context_args - A list of the context arguments to
        include in the keyword arguments.  See
        GraphQlContext.context_arg.
    basestring description - A description of the field, or None.
        GraphQL favors the Markdown format.
    bool is_deprecated - Whether the field is deprecated.
    basestring deprecation_reason - An indication of why the field is
        deprecated, or None.  This is None if is_deprecated is False.
    """
    def decorator(func):
        func._graphql_field_name = field_name
        func._graphql_field_type = field_type
        func._graphql_field_args = arguments
        func._graphql_field_context_args = context_args
        func._graphql_field_description = description
        func._graphql_field_is_deprecated = is_deprecated
        func._graphql_field_deprecation_reason = deprecation_reason
        return func
    return decorator


def graphql_attr_field(
        attr_name, field_name, field_type, description=None,
        is_deprecated=False, deprecation_reason=None):
    """Annotate a class's attribute as corresponding to a GraphQL field.

    The field appears in the GraphQL types for any of the class's
    subclasses that are annotated with graphql_object or
    graphql_interface.  The value of the field for a particular object
    is equal to the value of the attribute of the Python object, as in
    getattr.

    basestring attr_name - The name of the attribute.
    basestring field_name - The name of the GraphQL field.
    basestring field_type - The GraphQL type of the field's value.
    basestring description - A description of the field, or None.
        GraphQL favors the Markdown format.
    bool is_deprecated - Whether the field is deprecated.
    basestring deprecation_reason - An indication of why the field is
        deprecated, or None.  This is None if is_deprecated is False.
    """
    def decorator(cls):
        if '_graphql_attr_fields' not in cls.__dict__:
            cls._graphql_attr_fields = []
        cls._graphql_attr_fields.append({
            'attr': attr_name,
            'deprecationReason': deprecation_reason,
            'description': description,
            'fieldName': field_name,
            'fieldType': field_type,
            'isDeprecated': is_deprecated,
        })
        return cls
    return decorator


def graphql_custom_class_field(field_func):
    """Decorator that annotates a class exposing a field in GraphQL.

    The field appears in the GraphQL types for any of the class's
    subclasses that are annotated with graphql_object or
    graphql_interface.  It is not useful to decorate a function with
    graphql_custom_class_field directly.  Rather, the intended use is to
    to create an application-specific decorator that calls
    graphql_custom_class_field.

    The function field_func takes the class being decorated as an
    argument and returns a dictionary describing the GraphQL field.  The
    dictionary must have the following entries:

    args: A map from the names of the arguments to the field in GraphQL
        to their GraphQL types, as in the "arguments" argument to
        graphql_field.  See the comments for that argument.
    contextArgs: A list of the context arguments to include in the
        keyword arguments to methodName.  See
        GraphQlContext.context_arg.
    deprecationReason: A string indicating why the field is deprecated,
        or None.  This is None if isDeprecated is False.
    description: A string description of the field, or None.  GraphQL
        favors the Markdown format.
    fieldName: The name of the GraphQL field.
    fieldType: The GraphQL type of the field.
    isDeprecated: Whether the field is deprecated.
    methodName: The name of the method to call to obtain the field's
        value.
    partialArgs: The positional arguments to pass to methodName, as in
        GraphQlField.partial_args.
    partialKwargs: The additional keyword arguments to pass to
        methodName, as in GraphQlField.partial_kwargs.

    The reason graphql_custom_class_field takes a function that returns
    a dictionary rather than taking a dictionary is that decorator
    functions run in the global scope, so they should do as little work
    as possible.  Better to push whatever work we can into field_func.
    """
    def decorator(cls):
        if '_graphql_custom_class_field_funcs' not in cls.__dict__:
            cls._graphql_custom_class_field_funcs = []
        cls._graphql_custom_class_field_funcs.append(field_func)
        return cls
    return decorator


def graphql_root_field(
        field_name, field_type, arguments={}, context_args=[],
        description=None, is_deprecated=False, deprecation_reason=None):
    """Annotate a function as corresponding to a GraphQL root field.

    Decorator that annotates a function as corresponding to a GraphQL
    root query field; i.e. a field of the root query object.  The
    function must be a static method or a global function.  The value of
    the field is equal to the function's return value.  At present, we
    do not support annotating a function with multiple
    graphql_root_field annotations.

    basestring field_name - The name of the root field.
    basestring field_type - The GraphQL type of the field's value.
    dict<basestring, basestring> arguments - A map from the names of the
        arguments to the field in GraphQL to their GraphQL types, as in
        the "arguments" argument to graphql_field.  See the comments for
        that argument.
    list<basestring> context_args - A list of the context arguments to
        include in the keyword arguments.  See
        GraphQlContext.context_arg.
    basestring description - A description of the field, or None.
        GraphQL favors the Markdown format.
    bool is_deprecated - Whether the field is deprecated.
    basestring deprecation_reason - An indication of why the field is
        deprecated, or None.  This is None if is_deprecated is False.
    """
    def decorator(func):
        func._graphql_root_field_name = field_name
        func._graphql_root_field_type = field_type
        func._graphql_root_field_args = arguments
        func._graphql_root_field_context_args = context_args
        func._graphql_root_field_description = description
        func._graphql_root_field_is_deprecated = is_deprecated
        func._graphql_root_field_deprecation_reason = deprecation_reason
        return func
    return decorator


def graphql_mutation(
        field_name, field_type, arguments={}, context_args=[],
        description=None, is_deprecated=False, deprecation_reason=None):
    """Annotate a function as corresponding to a GraphQL mutation.

    Decorator that annotates a function as corresponding to a GraphQL
    mutation; i.e. a field of the root mutation object.  The function
    must be a static method or a global function.  The function performs
    the mutation and then returns its value.  At present, we do not
    support annotating a function with multiple graphql_mutation
    annotations.

    basestring field_name - The name of the mutation field.
    basestring field_type - The GraphQL type of the field's value.
    dict<basestring, basestring> arguments - A map from the names of the
        arguments to the field in GraphQL to their GraphQL types, as in
        the "arguments" argument to graphql_field.  See the comments for
        that argument.
    list<basestring> context_args - A list of the context arguments to
        include in the keyword arguments.  See
        GraphQlContext.context_arg.
    basestring description - A description of the mutation, or None.
        GraphQL favors the Markdown format.
    bool is_deprecated - Whether the mutation is deprecated.
    basestring deprecation_reason - An indication of why the mutation is
        deprecated, or None.  This is None if is_deprecated is False.
    """
    def decorator(func):
        func._graphql_mutation_name = field_name
        func._graphql_mutation_type = field_type
        func._graphql_mutation_args = arguments
        func._graphql_mutation_context_args = context_args
        func._graphql_mutation_description = description
        func._graphql_mutation_is_deprecated = is_deprecated
        func._graphql_mutation_deprecation_reason = deprecation_reason
        return func
    return decorator
