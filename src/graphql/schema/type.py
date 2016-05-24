from graphql import graphql_field
from graphql import graphql_object


@graphql_object('__Type', 'A GraphQL type')
class GraphQlType(object):
    """Base class for GraphQL types, e.g. object types and interfaces.

    Two GraphQlTypes are equal (as in == and !=) if they are the same
    type.
    """

    def is_subtype(self, other):
        """Return whether this is a subtype of "other".

        This is a subtype if every object of this type is also of type
        "other".

        GraphQlType other - The other type.
        return bool - Whether this is a subtype.
        """
        raise NotImplementedError('Subclasses must implement')

    def type_str(self):
        """Return the GraphQL type string for this type."""
        raise NotImplementedError('Subclasses must implement')

    def base_type(self):
        """Return the GraphQlBaseType this wraps.

        Return this if this is a GraphQlBaseType.
        """
        raise NotImplementedError('Subclasses must implement')

    @graphql_field(
        'name', 'String', {}, [],
        'The name of this, or None if this is not a base GraphQL type')
    def _type_name(self):
        """Return the name of this, or None if this is not a GraphQlBaseType.
        """
        return None

    @graphql_field('kind', '__TypeKind!', {}, [], 'The kind of this')
    def _type_kind(self):
        """Return a GraphQlTypeKind constant indicating the kind of this."""
        raise NotImplementedError('Subclasses must implement')

    @graphql_field(
        'description', 'String', {}, [],
        'A description of this type, or null.  GraphQL favors the Markdown '
        'format.')
    def _description(self):
        """Return a description of this type, or None.

        GraphQL favors the Markdown format.

        return basestring - The description.
        """
        raise NotImplementedError('Subclasses must implement')

    @graphql_field(
        'fields', '[__Field!]', {'includeDeprecated': 'Boolean'}, [],
        'The fields of this, or None if this is not an object or interface '
        'type.  This excludes any implicit fields, such as the "__typename" '
        'field.')
    def _explicit_field_descriptors(self, include_deprecated=False):
        """Return descriptions of the fields of this.

        Exclude any implicit fields that do not appear in
        __Type{fields}, such as the "__typename" field.  Return None if
        this is not an object or interface type.

        bool include_deprecated - Whether to include the deprecated
            fields in the result.
        return list<GraphQlFieldDescriptor> - The field descriptors.
        """
        return None

    @graphql_field(
        'interfaces', '[__Type!]', {}, [],
        'The interfaces this implements, or null if this is not an object '
        'type.')
    def _interfaces(self):
        """Return this interfaces this implements.

        Return None if this is not an object type.

        return list<GraphQlInterfaceType> - The interfaces.
        """
        return None

    @graphql_field(
        'possibleTypes', '[__Type!]', {}, [],
        'The object types that are of this type, or null if this is not an '
        'interface or union type.')
    def _possible_types(self):
        """Return the object types that are of this type.

        Return None if this is not an interface or union type.

        return list<GraphQlObjectType> - The object types.
        """
        return None

    @graphql_field(
        'enumValues', '[__EnumValue!]', {'includeDeprecated': 'Boolean'}, [],
        'The enumeration values of this, or null if this is not an '
        'enumeration type.  If includeDeprecated is true, the result excludes '
        'any deprecated values.')
    def _enum_values(self, include_deprecated=False):
        """Return the GraphQlEnumValues of this enum.

        Return None if this is not an enum type.

        bool include_deprecated - Whether to include the deprecated
            values in the result.
        return list<GraphQlEnumValue> - The values.
        """
        return None

    @graphql_field(
        'inputFields', '[__InputValue!]', {}, [],
        'The input object fields of this, or null if this is not an input '
        'object type.')
    def _input_fields(self):
        """Return the input object fields of this.

        Return None if this is not an input object type.

        return list<GraphQlInputValue> - The fields.
        """
        return None

    @graphql_field(
        'ofType', '__Type', {}, [],
        'The type this list or non-null type wraps, or null if this is not a '
        'list or non-null type.')
    def _wrapped_type(self):
        """Return the GraphQlType this list or non-null type wraps.

        Return None if this is not a list or non-null type.
        """
        return None
