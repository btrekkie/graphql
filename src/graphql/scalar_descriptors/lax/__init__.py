"""Contains lax GraphQlScalarDescriptors for the built-in scalar types.

Contains non-strictly validating GraphQlScalarDescriptors for the
built-in scalar types.  By "non-strictly validating", we mean that
Python methods and attributes that return field values of scalar types
need not return values strictly of those scalar types.  We will cast
them to the appropriate type.  For example, a field of type Int may
return the string '123'; we will cast this to the integer 123.
Non-strict validation only applies to result coercion, not input
coercion.
"""

from boolean import GraphQlLaxBooleanDescriptor
from float import GraphQlLaxFloatDescriptor
from id import GraphQlLaxIdDescriptor
from int import GraphQlLaxIntDescriptor
from string import GraphQlLaxStringDescriptor
