class GraphQlScalarDescriptor(object):
    """Description of a GraphQL scalar type.

    A scalar type is any type other than an enumeration whose GraphQL
    representation is limited to scalars.  GraphQlScalarDescriptor
    allows for standard types such as String and Float, as well as
    custom types, like timestamps and URLs.  Each
    GraphQlScalarDescriptor indicates how to convert between the JSON
    value representation of the scalar type and the Python object
    representation.  See also graphql_scalar.

    When it comes to the built-in scalar types (String, ID, Int, Float,
    and Boolean), the GraphQL parser and executor double-check the work
    of the GraphQlScalarDescriptor.  They make sure that in GraphQL
    documents and responses, the scalar representations of these types
    match those the GraphQL specification requires.  Furthermore, even
    for custom types, they make sure the scalar representations are one
    of the scalar types GraphQL supports.

    Public attributes:

    basestring name - The name of the GraphQL scalar type.
    """

    def __init__(self, name):
        self.name = name

    def graphql_to_python(self, value):
        """Return the Python object representation of the specified scalar.

        In other words, this performs input coercion.  Raise a TypeError
        or ValueError if "value" is not a valid representation of this
        type of scalar.  For example, if this a date type, and "value"
        is a string that is not a validly formatted date, this raises a
        ValueError.
        """
        raise NotImplementedError('Subclasses must override')

    def python_to_graphql(self, value):
        """Return the scalar representation of the specified Python object.

        In other words, this performs result coercion.  Raise a
        TypeError or ValueError if "value" is not a valid object for
        this type of scalar.  For example, if this is a timestamp type,
        this might return the ISO string representation of a given
        datetime object.  It would raise a TypeError if "value" is not a
        datetime.
        """
        raise NotImplementedError('Subclasses must override')
