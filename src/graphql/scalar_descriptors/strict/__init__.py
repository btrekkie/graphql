"""Contains strict GraphQlScalarDescriptors for the built-in scalar types.

Contains strictly validating GraphQlScalarDescriptors for the built-in
scalar types.  By "strictly validating", we mean that Python methods and
attributes that return field values of scalar types must return values
strictly of those scalar types.  For example, a field of type Int may
not return the string '123'.  Strict validation only applies to result
coercion, not input coercion.
"""

from boolean import GraphQlStrictBooleanDescriptor
from float import GraphQlStrictFloatDescriptor
from id import GraphQlStrictIdDescriptor
from int import GraphQlStrictIntDescriptor
from string import GraphQlStrictStringDescriptor
