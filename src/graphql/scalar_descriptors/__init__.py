"""Contains GraphQlScalarDescriptors for the built-in scalar types.

Depending on whether a project wants strict validation, the project may
use graphql.scalar_descriptors.strict or graphql.scalar_descriptors.lax,
e.g. in GraphQlSchemaFactory.create_from_modules.  The project also has
the option of defining its own GraphQlScalarDescriptors for the built-in
scalar types.  By "strict validation", we mean that Python methods and
attributes that return field values of scalar types must be strictly of
those scalar types.  For example, in strict validation, a field of type
Int may not return the string '123'.  Strict validation only applies to
result coercion, not input coercion.
"""
