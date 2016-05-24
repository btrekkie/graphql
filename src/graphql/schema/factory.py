import importlib
import inspect

from class_descriptor import GraphQlClassDescriptor
from enum_type import GraphQlEnumType
from field import GraphQlField
from field_descriptor import GraphQlFieldDescriptor
from func_descriptor import GraphQlFuncDescriptor
from graphql import GraphQlScalarDescriptor
from input_object_type import GraphQlInputObjectType
from interface_type import GraphQlInterfaceType
from non_null_type import GraphQlNonNullType
from object_type import GraphQlObjectType
from scalar_type import GraphQlScalarType
from schema import GraphQlSchema
from union_type import GraphQlUnionType


class GraphQlSchemaFactory(object):
    """Provides the ability to create GraphQlSchema instances.

    We create GraphQlSchemas from the graphql_* annotations in a given
    set of classes and functions.  Sample usage is as follows:

    # Return the name of the file that stores the schema
    schema_filename():
        return os.path.join(root_project_dir(), 'graphql_schema.json')

    # Compute the schema for the project and store it in
    # schema_filename()
    generate_schema():
        # Find all of the modules in the project
        modules = []
        for dir_path, sub_dirs, sub_files in (
                os.walk(root_project_dir())):
            for sub_file in sub_files:
                if (sub_file.endswith('.py') and
                        sub_file != '__init__.py'):
                    relative_filename = os.path.relpath(
                        os.path.join(dir_path, sub_file),
                        root_project_dir())
                    modules.append(
                        relative_filename.replace(os.sep, '.')[:-3])

        # Create the GraphQlSchema
        schema = GraphQlSchemaFactory.create_from_modules(
            modules +
            # Include the standard implementations of the built-in
            # scalar types
            ['graphql.scalar_descriptors.strict'])

        # Store the schema in schema_filename()
        with open(schema_filename(), 'w') as f:
            json.dump(schema.to_json(), f)

    # Return the GraphQlSchema for the project
    get_schema():
        with open(schema_filename(), 'r') as f:
            return GraphQlSchema.create_from_json(json.load(f))
    """

    # The names of the modules containing built-in GraphQL types for
    # introspection, i.e. types that must appear in every GraphQlSchema
    _BUILT_IN_MODULE_NAMES = ['graphql.executor', 'graphql.schema']

    @staticmethod
    def _add_parent_interfaces(
            cls, t, base_types, interface_classes_set, visited):
        """Find the parent interfaces of a GraphQlType.

        Recursive method that identifies the parent interfaces of a
        GraphQlObjectType or GraphQlInterfaceType, and associates the
        types with them using GraphQlBaseType.add_parent_type and
        GraphQlBaseType.add_child_type.  Specifically, this class finds
        all superclasses of "cls" that are in interface_classes_set that
        are reachable using child-to-parent links that do not pass
        through any classes in "visited".

        type cls - The class at which to begin searching.
        GraphQlBaseType t - The type for whose parents we are searching.
        dict<basestring, GraphQlBaseType> base_types - A map from the
            name of each base type to the type.
        set<type> interface_classes_set - A set of all interface types.
        set<type> visited - The classes we have visited.
        """
        if cls in visited:
            return
        visited.add(cls)
        if cls in interface_classes_set:
            interface_type = base_types[cls._graphql_interface_name]
            if t != interface_type:
                t.add_parent_type(interface_type)
                interface_type.add_child_type(t)
                return
        for parent_class in cls.__bases__:
            GraphQlSchemaFactory._add_parent_interfaces(
                parent_class, t, base_types, interface_classes_set, visited)

    @staticmethod
    def _validate_annotations(
            object_classes, interface_classes, scalar_classes,
            root_field_funcs):
        """Raise an exception if the specified objects do not validate.

        Raise an exception if the specified objects do not pass some
        basic validations - if they do not have the required
        annotations, if their names are not valid GraphQL identifiers,
        or if one of the classes is not of the appropriate type.

        list<type> object_classes - The classes of the GraphQL object
            types.
        list<type> interface_classes - The classes of the GraphQL
            interfaces.
        list<type> scalar_classes - The classes of the GraphQL scalar
            types.
        list<function> root_field_funcs - The functions for computing
            the values for GraphQL root fields.
        """
        # Concrete types
        from graphql.executor import GraphQlRootMutationObject
        from graphql.executor import GraphQlRootQueryObject
        for object_class in object_classes:
            if (object_class != GraphQlRootQueryObject and
                    object_class != GraphQlRootMutationObject):
                if '_graphql_object_name' not in object_class.__dict__:
                    raise ValueError(
                        '{:s} is not a GraphQL type'.format(
                            object_class.__name__))
                if (not GraphQlSchema.is_valid_identifier(
                        object_class._graphql_object_name)):
                    raise ValueError(
                        'The type name {:s} of {:s} is not a valid GraphQL '
                        'identifier'.format(
                            object_class._graphql_object_name,
                            object_class.__name__))

        # Interfaces
        for interface_class in interface_classes:
            if '_graphql_interface_name' not in interface_class.__dict__:
                raise ValueError(
                    '{:s} is not a GraphQL interface'.format(
                        interface_class.__name__))
            if (not GraphQlSchema.is_valid_identifier(
                    interface_class._graphql_interface_name)):
                raise ValueError(
                    'The type name {:s} of {:s} is not a valid GraphQL '
                    'identifier'.format(
                        interface_class._graphql_interface_name,
                        interface_class.__name__))

        # Scalar types
        for scalar_class in scalar_classes:
            if '_graphql_scalar_name' not in scalar_class.__dict__:
                raise ValueError(
                    '{:s} is not a GraphQL scalar'.format(
                        scalar_class.__name__))
            if not issubclass(scalar_class, GraphQlScalarDescriptor):
                raise TypeError(
                    '{:s} is annotated with graphql_scalar, but it does not '
                    'subclass GraphQlScalarDescriptor'.format(
                        scalar_class.__name__))
            if (not GraphQlSchema.is_valid_identifier(
                    scalar_class._graphql_scalar_name)):
                raise ValueError(
                    'The type name {:s} of {:s} is not a valid GraphQL '
                    'identifier'.format(
                        scalar_class._graphql_scalar_name,
                        scalar_class.__name__))

        # Root fields
        for root_field_func in root_field_funcs:
            if not hasattr(root_field_func, '_graphql_root_field_name'):
                raise ValueError(
                    '{:s} is not a GraphQL root field'.format(
                        root_field_func.__name__))
            if (not GraphQlSchema.is_valid_identifier(
                    root_field_func._graphql_root_field_name)):
                raise ValueError(
                    'The root field name {:s} of {:s} is not a valid GraphQL '
                    'identifier'.format(
                        root_field_func._graphql_root_field_name,
                        root_field_func.__name__))

    @staticmethod
    def _type_name(object_class, query_type_name, mutation_type_name):
        """Return the GraphQL object type name of the specified class.

        Assume it has an object type name.

        type object_class - The class.
        basestring query_type_name - The name of the GraphQL type of the
            root query object.
        basestring mutation_type_name - The name of the GraphQL type of
            the root mutation object, if any.
        return basestring - The object type name.
        """
        from graphql.executor import GraphQlRootMutationObject
        from graphql.executor import GraphQlRootQueryObject
        if object_class == GraphQlRootQueryObject:
            return query_type_name
        elif object_class == GraphQlRootMutationObject:
            return mutation_type_name
        else:
            return object_class._graphql_object_name

    @staticmethod
    def _enum_types(enum_funcs):
        """Return the types for functions annotated with graphql_enum.

        list<() -> dict<basestring, basestring>> enum_funcs - The
            functions.
        return list<GraphQlEnumType> - The types.
        """
        enum_types = []
        for enum_func in enum_funcs:
            enum_name = enum_func._graphql_enum_name

            # Validate the enum values
            func_descriptor = GraphQlFuncDescriptor.create_from_func(enum_func)
            graphql_to_python = func_descriptor.load_func()()
            python_to_graphql = {}
            for graphql, python in graphql_to_python.iteritems():
                if (graphql == 'true' or graphql == 'false' or
                        graphql == 'null'):
                    raise ValueError(
                        'The identifier {:s} is reserved and may not appear '
                        'in the enum type {:s}'.format(graphql, enum_name))
                if python in python_to_graphql:
                    raise ValueError(
                        u'Each Python value must correspond to exactly one '
                        'GraphQL enum value.  In the enum type {:s}, {:s} '
                        'corresponds to both {:s} and {:s}.'.format(
                            enum_name, str(python), python_to_graphql[python],
                            graphql))
                python_to_graphql[python] = graphql

            enum_types.append(
                GraphQlEnumType(
                    enum_name, enum_func._graphql_enum_description,
                    func_descriptor))
        return enum_types

    @staticmethod
    def _field(
            type_name, field_name, field_type_str, arguments, description,
            is_deprecated, deprecation_reason, method_name, partial_args,
            partial_kwargs, context_args, attr, base_types):
        """Return a GraphQlField object for a field annotation.

        basestring type_name - The name of the type of object to which
            the field belongs.  Note that this is not the same thing as
            the type of the field's value.
        basestring field_name - The name of the field.
        basestring field_type_str - The GraphQL type string of the type
            of the value of the field.
        dict<basestring, basestring> arguments - A map from the names of
            the arguments to the field in GraphQL to their GraphQL
            types, as in the "arguments" argument to graphql_field.  See
            the comments for that argument.
        basestring description - A description of the field, or None.
            GraphQL favors the Markdown format.
        bool is_deprecated - Whether the field is deprecated.
        basestring deprecation_reason - An indication of why the field
            is deprecated, or None.  This is None if is_deprecated is
            False.
        basestring method_name - The name of the method for obtaining
            the field's value.  This is None if we obtain the field's
            value using an attribute.
        tuple partial_args - The positional arguments to pass to
            method_name, as in GraphQlField.partial_args.
        dict<basestring, object> partial_kwargs - The additional keyword
            arguments to pass to method_name, as in
            GraphQlField.partial_kwargs.
        list<basestring> context_args - A list of the context arguments
            to include in the keyword arguments to method_name.  This is
            None if we obtain the field's value using an attribute.  See
            GraphQlContext.context_arg.
        basestring attr - The name of the attribute containing the
            field's value, as in getattr.  This is None if we obtain the
            field's value using a method.
        dict<basestring, GraphQlBaseType> base_types - A map from the
            name of each base type to the type.
        return GraphQlField - The field.
        """
        # Compute the arguments
        if (attr is not None and
                (arguments or method_name is not None or
                    partial_args is not None or partial_kwargs is not None or
                    context_args is not None)):
            raise ValueError(
                'The GraphQL field {:s}{{{:s}}} may not be specified using an '
                'attribute unless it has no method name or arguments'.format(
                    type_name, field_name))
        arg_types = {}
        for arg_name, arg_type_str in arguments.iteritems():
            arg_types[arg_name] = GraphQlSchema.parse_type(
                arg_type_str, base_types, True, False,
                'the {:s} argument to the field {:s}{{{:s}}}'.format(
                    arg_name, type_name, field_name))

        # Create the GraphQlField
        field_type = GraphQlSchema.parse_type(
            field_type_str, base_types, False, True,
            '{:s}{{{:s}}}'.format(type_name, field_name))
        descriptor = GraphQlFieldDescriptor(
            field_name, field_type, arg_types, description, is_deprecated,
            deprecation_reason)
        return GraphQlField(
            descriptor, method_name, partial_args, partial_kwargs,
            context_args, attr)

    @staticmethod
    def _assert_can_override(
            sub_field_descriptor, super_field_descriptor,
            sub_class, super_class):
        """Raise an exception if one field cannot override another.

        Raise an exception if the definition of sub_field_descriptor is
        incompatible with super_field_descriptor - if the former may not
        override the latter.  This condition differs from simple
        equality.  For example, if an interface declares a field "foo"
        of type Base, an implementation of this interface may declare a
        field "foo" of type Derived, where Derived is a subtype of Base.

        Assume that the GraphQlBaseType.parent_types and
        GraphQlBaseType.child_types fields have been computed for all
        types.

        GraphQlFieldDescriptor sub_field_descriptor - The candidate
            overriding field.
        GraphQlFieldDescriptor super_field_descriptor - The candidate
            overridden field.
        type sub_class - The class containing the field indicated by
            sub_field_descriptor.
        type super_class - The class containing the field indicated by
            super_field_descriptor.
        """
        # Check whether the field types are compatible
        if (not sub_field_descriptor.field_type.is_subtype(
                super_field_descriptor.field_type)):
            raise ValueError(
                'The {:s} class has a GraphQL field annotation for the {:s} '
                "field, but its type is incompatible with the {:s} class's "
                'annotation for this field.  {:s} is not a subtype of '
                '{:s}.'.format(
                    sub_class.__name__, sub_field_descriptor.name,
                    super_class.__name__,
                    sub_field_descriptor.field_type.type_str(),
                    super_field_descriptor.field_type.type_str()))

        # Check whether the arguments are compatible
        for arg_name, super_arg_type in (
                super_field_descriptor.args.iteritems()):
            if arg_name not in sub_field_descriptor.args:
                raise ValueError(
                    'The {:s} class has a GraphQL field annotation for the '
                    '{:s} field, but it does not support the {:s} argument as '
                    "in the {:s} class's annotation for this field".format(
                        sub_class.__name__, sub_field_descriptor.name,
                        arg_name, super_class.__name__))
            sub_arg_type = sub_field_descriptor.args[arg_name]
            if sub_arg_type != super_arg_type:
                raise ValueError(
                    'The {:s} class has a GraphQL field annotation for the '
                    '{:s} field, but it specifies a different type for the '
                    "{:s} argument than the {:s} class's annotation does for "
                    'this field'.format(
                        sub_class.__name__, sub_field_descriptor.name,
                        arg_name, super_class.__name__))
        for arg_name, arg_type in sub_field_descriptor.args.iteritems():
            if (arg_name not in super_field_descriptor.args and
                    isinstance(arg_type, GraphQlNonNullType)):
                raise ValueError(
                    'The {:s} class has a GraphQL field annotation for the '
                    '{:s} field, but it includes the required argument {:s}, '
                    "which is not available in the {:s} class's annotation "
                    'for this field'.format(
                        sub_class.__name__, sub_field_descriptor.name,
                        arg_name, super_class.__name__))

    @staticmethod
    def _fields(cls, type_name, base_types):
        """Return the fields declared for an object or interface type.

        Assume that the GraphQlBaseType.parent_types and
        GraphQlBaseType.child_types fields have been computed for all
        types.

        type cls - The class for instances of the type.
        basestring type_name - The name of the type.
        dict<basestring, GraphQlBaseType> base_types - A map from the
            name of each base type to the type.
        return list<GraphQlField> - The fields.
        """
        fields = []
        descriptors = {}
        classes = {}
        method_names = {}
        attrs = {}
        for parent_class in inspect.getmro(cls):
            class_fields = []

            # Compute the fields from the class's decorators
            attr_fields = getattr(parent_class, '_graphql_attr_fields', [])
            for attr_field in attr_fields:
                class_fields.append(
                    GraphQlSchemaFactory._field(
                        type_name, attr_field['fieldName'],
                        attr_field['fieldType'], {}, attr_field['description'],
                        attr_field['isDeprecated'],
                        attr_field['deprecationReason'], None, None, None,
                        None, attr_field['attr'], base_types))
            class_custom_fields_funcs = getattr(
                parent_class, '_graphql_custom_class_field_funcs', [])
            for func in class_custom_fields_funcs:
                field_info = func(parent_class)
                class_fields.append(
                    GraphQlSchemaFactory._field(
                        type_name, field_info['fieldName'],
                        field_info['fieldType'], field_info['args'],
                        field_info['description'], field_info['isDeprecated'],
                        field_info['deprecationReason'],
                        field_info['methodName'], field_info['partialArgs'],
                        field_info['partialKwargs'], field_info['contextArgs'],
                        None, base_types))

            # Compute the fields from the class's method's decorators
            for key, value in parent_class.__dict__.iteritems():
                if callable(value) and hasattr(value, '_graphql_field_name'):
                    class_fields.append(
                        GraphQlSchemaFactory._field(
                            type_name, value._graphql_field_name,
                            value._graphql_field_type,
                            value._graphql_field_args,
                            value._graphql_field_description,
                            value._graphql_field_is_deprecated,
                            value._graphql_field_deprecation_reason, key, (),
                            {}, value._graphql_field_context_args, None,
                            base_types))

            # Validate and add the fields
            for field in class_fields:
                name = field.descriptor.name
                if not GraphQlSchema.is_valid_identifier(name):
                    raise ValueError(
                        'The field name {:s} of the method {:s}.{:s} is not a '
                        'valid GraphQL identifier'.format(
                            name, parent_class.__name__, key))

                other_field_descriptor = descriptors.get(name)
                if other_field_descriptor is None:
                    fields.append(field)
                    descriptors[name] = field.descriptor
                    classes[name] = parent_class
                    method_names[name] = field.method_name
                    attrs[name] = field.attr
                elif (field.method_name != method_names[name] or
                        field.attr != attrs[name]):
                    raise ValueError(
                        'Duplicate field {:s}{{{:s}}}'.format(
                            type_name, field.descriptor.name))
                else:
                    GraphQlSchemaFactory._assert_can_override(
                        other_field_descriptor, field.descriptor,
                        classes[name], parent_class)
        return fields

    @staticmethod
    def _root_fields(root_field_funcs, base_types):
        """Return the GraphQlFields for the root query object.

        list<function> root_field_funcs - The functions for computing the
            values for the root fields.
        dict<basestring, GraphQlBaseType> base_types - A map from the
            name of each base type to the type.
        return list<GraphQlField> - The root fields.
        """
        root_fields = []
        for root_field_func in root_field_funcs:
            # Compute the GraphQlFieldDescriptor
            field_name = root_field_func._graphql_root_field_name
            if field_name in root_fields:
                raise RuntimeError(
                    'There are multiple graphql_root_field annotations with '
                    'the name {:s}'.format(field_name))
            field_type_str = root_field_func._graphql_root_field_type
            field_type = GraphQlSchema.parse_type(
                field_type_str, base_types, False, True,
                'the root field {:s}'.format(field_name))
            args = {}
            arg_type_strs = root_field_func._graphql_root_field_args
            for arg_name, arg_type_str in arg_type_strs.iteritems():
                args[arg_name] = GraphQlSchema.parse_type(
                    arg_type_str, base_types, True, False,
                    'the {:s} argument to the root field {:s}'.format(
                        arg_name, field_name))
            field_descriptor = GraphQlFieldDescriptor(
                field_name, field_type, args,
                root_field_func._graphql_root_field_description,
                root_field_func._graphql_root_field_is_deprecated,
                root_field_func._graphql_root_field_deprecation_reason)

            # Compute the GraphQlField
            func_descriptor = GraphQlFuncDescriptor.create_from_func(
                root_field_func)
            root_fields.append(
                GraphQlField.create_from_method(
                    field_descriptor, 'field', (
                        func_descriptor.module_name,
                        func_descriptor.class_name,
                        func_descriptor.func_name),
                    {}, root_field_func._graphql_root_field_context_args))
        return root_fields

    @staticmethod
    def _mutations(mutation_funcs, base_types):
        """Return the GraphQlFields for the mutations.

        list<function> mutations_funcs - The functions for executing
            GraphQL mutations.
        dict<basestring, GraphQlBaseType> base_types - A map from the
            name of each base type to the type.
        return list<GraphQlField> - The mutations.
        """
        mutations = []
        for mutation_func in mutation_funcs:
            # Compute the GraphQlFieldDescriptor
            field_name = mutation_func._graphql_mutation_name
            if field_name in mutations:
                raise RuntimeError(
                    'There are multiple graphql_mutation annotations with the '
                    'name {:s}'.format(field_name))
            field_type_str = mutation_func._graphql_mutation_type
            field_type = GraphQlSchema.parse_type(
                field_type_str, base_types, False, True,
                'the mutation {:s}'.format(field_name))
            args = {}
            arg_type_strs = mutation_func._graphql_mutation_args
            for arg_name, arg_type_str in arg_type_strs.iteritems():
                args[arg_name] = GraphQlSchema.parse_type(
                    arg_type_str, base_types, True, False,
                    'the {:s} argument to the mutation {:s}'.format(
                        arg_name, field_name))
            field_descriptor = GraphQlFieldDescriptor(
                field_name, field_type, args,
                mutation_func._graphql_mutation_description,
                mutation_func._graphql_mutation_is_deprecated,
                mutation_func._graphql_mutation_deprecation_reason)

            # Compute the GraphQlField
            func_descriptor = GraphQlFuncDescriptor.create_from_func(
                mutation_func)
            mutations.append(
                GraphQlField.create_from_method(
                    field_descriptor, 'execute_mutation', (
                        func_descriptor.module_name,
                        func_descriptor.class_name,
                        func_descriptor.func_name),
                    {}, mutation_func._graphql_mutation_context_args))
        return mutations

    @staticmethod
    def _assert_no_cycle(t, path, path_set, visited):
        """Raise if there is a cycle of GraphQlUnionTypes.

        Raise if there is a cycle of union types starting at "t"
        consisting of parent-to-child links that do not pass through
        types in "visited".  Add any types this visits to "visited".

        GraphQlUnionType t - The type at which to start the search.
        list<GraphQlUnionType> path - The types in the current path,
            excluding the last edge to "t".  _assert_no_cycle may modify
            "path", but it must restore the original value before it
            finishes.
        set<GraphQlUnionType> path_set - Equivalent to set(path).
            _assert_no_cycle may modify path_set, but it must restore
            the original value before it finishes.
        set<GraphQlUnionType> visited - The types we have visited.
        """
        if t in path_set:
            cycle = list([t2.name for t2 in path[path.index(t):]]) + [t.name]
            raise RuntimeError(
                'Union declarations contain a cycle: {:s}'.format(
                    ' => '.join(cycle)))
        if t not in visited:
            visited.add(t)
            path.append(t)
            path_set.add(t)
            for child in t.child_types:
                if isinstance(child, GraphQlUnionType):
                    GraphQlSchemaFactory._assert_no_cycle(
                        child, path, path_set, visited)
            path.pop()
            path_set.remove(t)

    @staticmethod
    def _create(
            object_classes, interface_classes, scalar_classes,
            root_field_funcs, mutation_funcs, input_object_funcs, union_funcs,
            enum_funcs, query_type_name, mutation_type_name):
        """Return a new GraphQlSchema for the specified classes and functions.

        Return a new GraphQlSchema for the specified classes and
        functions, annotated with graphql_* decorators.  Raise an
        exception if we detect anything wrong with the annotations.

        list<type> object_classes - The classes of the GraphQL object
            types.
        list<type> interface_classes - The classes of the GraphQL
            interfaces.
        list<type> scalar_classes - The classes of the GraphQL scalar
            types.
        list<function> root_field_funcs - The functions for computing
            the values for GraphQL root fields.
        list<function> mutation_funcs - The functions for executing
            GraphQL mutations.
        list<() -> dict<basestring, basestring>> input_object_funcs -
            The functions for the input object types, decorated with
            graphql_input_object.
        list<() -> list<basestring>> union_funcs - The functions for the
            union types, decorated with graphql_union.
        list<() -> dict<basestring, mixed>> enum_funcs - The functions
            for the enum types, decorated with graphql_enum.
        basestring query_type_name - The name of the GraphQL type of the
            root query object.
        basestring mutation_type_name - The name of the GraphQL type of
            the root mutation object, if any.
        return GraphQlSchema - The schema.
        """
        from graphql.executor import GraphQlRootMutationObject
        from graphql.executor import GraphQlRootQueryObject
        GraphQlSchemaFactory._validate_annotations(
            object_classes, interface_classes, scalar_classes,
            root_field_funcs)

        # Create the GraphQlBaseType objects
        interface_classes_set = set(interface_classes)
        base_types = {}
        object_types = {}
        interface_types = {}
        input_object_types = {}
        union_types = {}
        for scalar_class in scalar_classes:
            scalar_name = scalar_class._graphql_scalar_name
            if scalar_name in base_types:
                raise RuntimeError(
                    'There are multiple GraphQL type annotations with the '
                    'name {:s}'.format(scalar_name))
            scalar_type = GraphQlScalarType(
                scalar_name, scalar_class._graphql_scalar_description,
                GraphQlClassDescriptor.create_from_class(scalar_class))
            base_types[scalar_name] = scalar_type
        for object_class in object_classes:
            type_name = GraphQlSchemaFactory._type_name(
                object_class, query_type_name, mutation_type_name)
            if object_class == GraphQlRootQueryObject:
                description = 'The root object for GraphQL queries'
            elif object_class == GraphQlRootMutationObject:
                description = 'The root object for GraphQL mutation operations'
            else:
                description = object_class._graphql_object_description
            if type_name in base_types:
                raise RuntimeError(
                    'There are multiple GraphQL type annotations with the '
                    'name {:s}'.format(type_name))
            class_descriptor = GraphQlClassDescriptor.create_from_class(
                object_class)
            t = GraphQlObjectType(type_name, description, class_descriptor)
            base_types[type_name] = t
            object_types[type_name] = t
        for interface_class in interface_classes:
            interface_name = interface_class._graphql_interface_name
            if interface_name in base_types:
                raise RuntimeError(
                    'There are multiple GraphQL type annotations with the '
                    'name {:s}'.format(type_name))
            interface_type = GraphQlInterfaceType(
                interface_name, interface_class._graphql_interface_description)
            base_types[interface_name] = interface_type
            interface_types[interface_name] = interface_type
        for enum_type in GraphQlSchemaFactory._enum_types(enum_funcs):
            if enum_type.name in base_types:
                raise RuntimeError(
                    'There are multiple GraphQL type annotations with the '
                    'name {:s}'.format(enum_type.name))
            base_types[enum_type.name] = enum_type
        for func in input_object_funcs:
            name = func._graphql_input_object_name
            if name in base_types:
                raise RuntimeError(
                    'There are multiple GraphQL type annotations with the '
                    'name {:s}'.format(name))
            input_object_type = GraphQlInputObjectType(
                name, func._graphql_input_object_description)
            input_object_types[name] = input_object_type
            base_types[name] = input_object_type
        for func in union_funcs:
            name = func._graphql_union_name
            if name in base_types:
                raise RuntimeError(
                    'There are multiple GraphQL type annotations with the '
                    'name {:s}'.format(name))
            union_type = GraphQlUnionType(
                name, func._graphql_union_description)
            union_types[name] = union_type
            base_types[name] = union_type

        # Compute parent-child relationships.  We must do this before computing
        # the fields, as the _fields method requires this information.
        for object_class in object_classes:
            type_name = GraphQlSchemaFactory._type_name(
                object_class, query_type_name, mutation_type_name)
            GraphQlSchemaFactory._add_parent_interfaces(
                object_class, base_types[type_name], base_types,
                interface_classes_set, set())
        for interface_class in interface_classes:
            GraphQlSchemaFactory._add_parent_interfaces(
                interface_class,
                base_types[interface_class._graphql_interface_name],
                base_types, interface_classes_set, set())
        for union_func in union_funcs:
            union_type = base_types[union_func._graphql_union_name]
            func_descriptor = GraphQlFuncDescriptor.create_from_func(
                union_func)
            for name in func_descriptor.load_func()():
                if name not in base_types:
                    raise RuntimeError(
                        'The union {:s} contains the non-existent type '
                        '{:s}'.format(union_type.name, name))
                t = base_types[name]
                if (not isinstance(
                        t, (
                            GraphQlInterfaceType,
                            GraphQlObjectType,
                            GraphQlUnionType))):
                    raise RuntimeError(
                        'The union {:s} contains the type {:s}, but that is '
                        'not an object, interface, or union type'.format(
                            union_type.name, name))
                union_type.add_child_type(t)
                t.add_parent_type(union_type)

        # Check for cycles in union types
        visited = set()
        for union_type in union_types.itervalues():
            GraphQlSchemaFactory._assert_no_cycle(
                union_type, [], set(), visited)

        # Create the GraphQlFieldDescriptors and GraphQlFields, and reference
        # them in the appropriate type objects
        for interface_class in interface_classes:
            type_name = interface_class._graphql_interface_name
            fields = GraphQlSchemaFactory._fields(
                interface_class, type_name, base_types)
            t = base_types[type_name]
            for field in fields:
                t.add_field_descriptor(field.descriptor)
        for object_class in object_classes:
            type_name = GraphQlSchemaFactory._type_name(
                object_class, query_type_name, mutation_type_name)
            fields = GraphQlSchemaFactory._fields(
                object_class, type_name, base_types)
            t = base_types[type_name]
            for field in fields:
                t.add_field(field)

        # Add the fields to the GraphQlInputObjects
        for func in input_object_funcs:
            name = func._graphql_input_object_name
            input_object_type = input_object_types[name]
            func_descriptor = GraphQlFuncDescriptor.create_from_func(func)
            for field_name, field_type_str in (
                    func_descriptor.load_func()().iteritems()):
                t = GraphQlSchema.parse_type(
                    field_type_str, base_types, True, False,
                    '{:s}.{:s}'.format(name, field_name))
                input_object_type.add_field(field_name, t)

        # Add the root query fields
        if query_type_name not in object_types:
            raise RuntimeError(
                'There must be an object type named {:s}, because that is the '
                'root query type name'.format(query_type_name))
        root_type = object_types[query_type_name]
        root_fields = GraphQlSchemaFactory._root_fields(
            root_field_funcs, base_types)
        for root_field in root_fields:
            root_type.add_field(root_field)

        # Add the mutations
        if mutation_type_name is not None:
            if mutation_type_name not in object_types:
                raise RuntimeError(
                    'There must be an object type named {:s}, because that is '
                    'the root mutation type name'.format(mutation_type_name))
            mutation_type = object_types[mutation_type_name]
            mutations = GraphQlSchemaFactory._mutations(
                mutation_funcs, base_types)
            for mutation in mutations:
                mutation_type.add_field(mutation)
        elif mutation_funcs:
            raise RuntimeError(
                'If there are mutations, the mutation type name may not be '
                'None')

        return GraphQlSchema(base_types, query_type_name, mutation_type_name)

    @staticmethod
    def _add_superclasses(cls, classes):
        """Add superclasses of "cls" to "classes".

        Add all of the classes for which there is a path of
        subclass-to-superclass links starting at "cls" that does not
        pass through any class in "classes" to "classes".

        type cls - The class at which to start the search.
        set<type> classes - The set to which to add the superclasses.
        """
        if cls not in classes:
            classes.add(cls)
            for parent_class in cls.__bases__:
                GraphQlSchemaFactory._add_superclasses(parent_class, classes)

    @staticmethod
    def _create_from_classes_and_funcs(
            classes, funcs, query_type_name, mutation_type_name):
        """Return a new GraphQlSchema for the specified classes and functions.

        Return a new GraphQlSchema for the graphql_* annotations on the
        specified classes and functions.  Assume they include all
        built-in types.  Raise if we detect anything wrong with the
        annotations.

        list<type> classes - The classes.
        list<func> funcs - The functions.
        basestring query_type_name - The name of the GraphQL type of the
            root query object.
        basestring mutation_type_name - The name of the GraphQL type of
            the root mutation object, if any.
        return GraphQlSchema - The schema.
        """
        from graphql.executor import GraphQlRootMutationObject
        from graphql.executor import GraphQlRootQueryObject

        # Compute a set containing "classes" and superclasses of "classes"
        classes_set = set()
        for cls in classes:
            GraphQlSchemaFactory._add_superclasses(cls, classes_set)

        object_classes = []
        interface_classes = []
        scalar_classes = []
        root_field_funcs = []
        mutation_funcs = []
        input_object_funcs = []
        union_funcs = []
        enum_funcs = []

        # Check the classes
        for cls in classes_set:
            if '_graphql_object_name' in cls.__dict__:
                object_classes.append(cls)
            if '_graphql_interface_name' in cls.__dict__:
                interface_classes.append(cls)
            if '_graphql_scalar_name' in cls.__dict__:
                scalar_classes.append(cls)
            for key, value in cls.__dict__.iteritems():
                if (isinstance(value, staticmethod) and
                        hasattr(getattr(cls, key), '__get__')):
                    func = getattr(cls, key).__get__(None, cls)
                    if hasattr(func, '_graphql_root_field_name'):
                        root_field_funcs.append(func)
                    if hasattr(func, '_graphql_mutation_name'):
                        mutation_funcs.append(func)
                    if hasattr(func, '_graphql_input_object_name'):
                        input_object_funcs.append(func)
                    if hasattr(func, '_graphql_union_name'):
                        union_funcs.append(func)
                    if hasattr(func, '_graphql_enum_name'):
                        enum_funcs.append(func)
        object_classes.append(GraphQlRootQueryObject)
        if mutation_type_name is not None:
            object_classes.append(GraphQlRootMutationObject)

        # Check the functions
        for func in funcs:
            if hasattr(func, '_graphql_root_field_name'):
                root_field_funcs.append(func)
            if hasattr(func, '_graphql_mutation_name'):
                mutation_funcs.append(func)
            if hasattr(func, '_graphql_input_object_name'):
                input_object_funcs.append(func)
            if hasattr(func, '_graphql_union_name'):
                union_funcs.append(func)
            if hasattr(func, '_graphql_enum_name'):
                enum_funcs.append(func)

        return GraphQlSchemaFactory._create(
            object_classes, interface_classes, scalar_classes,
            root_field_funcs, mutation_funcs, input_object_funcs, union_funcs,
            enum_funcs, query_type_name, mutation_type_name)

    @staticmethod
    def create_from_classes_and_funcs(
            classes, funcs,
            query_type_name=GraphQlSchema._DEFAULT_QUERY_TYPE_NAME,
            mutation_type_name=GraphQlSchema._DEFAULT_MUTATION_TYPE_NAME):
        """Return a new GraphQlSchema for the specified classes and functions.

        Return a new GraphQlSchema for the graphql_* annotations on the
        specified classes and functions, along with the built-in GraphQL
        types for introspection.  Note that this does not automatically
        include the classes in graphql.scalar_descriptors.strict.  Raise
        if we detect anything wrong with the annotations.

        list<type> classes - The classes.
        list<func> funcs - The functions.
        basestring query_type_name - The name of the GraphQL type of the
            root query object.
        basestring mutation_type_name - The name of the GraphQL type of
            the root mutation object, if any.
        return GraphQlSchema - The schema.
        """
        classes_set = set(classes)
        funcs_set = set(funcs)
        for module_name in GraphQlSchemaFactory._BUILT_IN_MODULE_NAMES:
            module = importlib.import_module(module_name)
            for class_name, cls in inspect.getmembers(module, inspect.isclass):
                classes_set.add(cls)
            for name, func in inspect.getmembers(module, inspect.isfunction):
                funcs_set.add(func)
        return GraphQlSchemaFactory._create_from_classes_and_funcs(
            list(classes_set), list(funcs_set),
            query_type_name, mutation_type_name)

    @staticmethod
    def create_from_modules(
            module_names,
            query_type_name=GraphQlSchema._DEFAULT_QUERY_TYPE_NAME,
            mutation_type_name=GraphQlSchema._DEFAULT_MUTATION_TYPE_NAME):
        """Return a new GraphQlSchema for the specified modules.

        Return a new GraphQlSchema for the graphql_* annotations in the
        specified modules, along with built-in GraphQL types for
        introspection.  Note that this does not automatically include
        graphql.scalar_descriptors.strict.  Raise if we detect anything
        wrong with the annotations.  This method imports the modules.

        list<basestring> module_names - The names of the modules.
        basestring query_type_name - The name of the GraphQL type of the
            root query object.
        basestring mutation_type_name - The name of the GraphQL type of
            the root mutation object, if any.
        return GraphQlSchema - The schema.
        """
        # Find all of the classes and functions in the modules
        classes = set()
        funcs = set()
        for module_name in (
                module_names + GraphQlSchemaFactory._BUILT_IN_MODULE_NAMES):
            module = importlib.import_module(module_name)
            for class_name, cls in inspect.getmembers(module, inspect.isclass):
                classes.add(cls)
            for name, func in inspect.getmembers(module, inspect.isfunction):
                funcs.add(func)
        return GraphQlSchemaFactory._create_from_classes_and_funcs(
            list(classes), list(funcs), query_type_name, mutation_type_name)
