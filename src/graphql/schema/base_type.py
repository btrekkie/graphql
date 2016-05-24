from type import GraphQlType


class GraphQlBaseType(GraphQlType):
    """Abstract base class for GraphQL base types.

    A base type is a type other than a list or non-null type.

    Public attributes:

    list<GraphQlBaseType> child_types - The child interfaces, objects,
        and unions.  If this is an interface, child_types is the
        subinterfaces and concrete implementations of this.  If this is
        a union, child_types is the object types, interfaces, and unions
        that comprise this.  If this is an object type, child_types is
        an empty list.  child_types includes immediate children only,
        i.e. it does include anything that is a descendant of a child.
        It does not include this.
    basestring description - A description of this type, or None.
        GraphQL favors the Markdown format.
    basestring name - The name of the type.
    list<GraphQlBaseType> parent_types - The parent types, i.e. the
        inverse of child_types.  This includes immediate parents only,
        i.e. it does not include anything that is an ancestor of a
        parent.  It does not include this.
    """

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.parent_types = []
        self.child_types = []

    def add_parent_type(self, parent_type):
        """Equivalent implementation is contractual."""
        self.parent_types.append(parent_type)

    def add_child_type(self, child_type):
        """Equivalent implementation is contractual."""
        self.child_types.append(child_type)

    def _find_parent_type(self, other, visited):
        """Recursive implementation of is_subtype.

        Return whether there is a path using child-to-parent links from
        "self" to "other", without passing through any types in
        "visited".  Add any types this visits to "visited".

        GraphQlType other - The candidate parent type.
        set<GraphQlBaseType> visited - The types we have visited.
        return bool - Whether "other" is a supertype.
        """
        if self in visited:
            return False
        visited.add(self)
        if self == other:
            return True
        for parent in self.parent_types:
            if parent._find_parent_type(other, visited):
                return True
        return False

    def is_subtype(self, other):
        return self._find_parent_type(other, set())

    def _add_ancestor_types(self, ancestor_types):
        """Recursive implementation of ancestor_types.

        Add the strict supertypes of this to ancestor_types, excluding
        those supertypes we cannot reach using child-to-parent links
        that do not pass through ancestor_types.

        set<GraphQlBaseType> ancestor_types - The set to which to add
            the ancestor types.
        """
        for parent in self.parent_types:
            if parent not in ancestor_types:
                ancestor_types.add(parent)
                parent._add_ancestor_types(ancestor_types)

    def ancestor_types(self):
        """Return a list of the ancestor types of this, excluding self.

        See parent_types.
        """
        ancestor_types = set()
        self._add_ancestor_types(ancestor_types)
        return list(ancestor_types)

    def _add_leaf_types(self, leaf_types, visited):
        """Recursive implementation of leaf_types.

        Add any types reachable using parent-to-child links from "self",
        without passing through any nodes in "visited", that do not have
        any children to leaf_types.  Add any types this visits to
        "visited".

        list<GraphQlBaseType> leaf_types - The leaf types.
        set<GraphQlBaseType> visited - The types we have visited.
        """
        if self not in visited:
            visited.add(self)
            if not self.child_types:
                leaf_types.append(self)
            else:
                for child_type in self.child_types:
                    child_type._add_leaf_types(leaf_types, visited)

    def leaf_types(self):
        """Return the descendant types of this that do not have any children.

        return list<GraphQlBaseType> - The descendant types.
        """
        leaf_types = []
        self._add_leaf_types(leaf_types, set())
        return leaf_types

    def type_str(self):
        return self.name

    def base_type(self):
        return self

    def field_descriptor(self, name):
        """Return the GraphQlFieldDescriptor for the specified field.

        Return the GraphQlFieldDescriptor for the field with the
        specified name on this object.  Raise a ValueError if this has
        no such field, this is a scalar, enum, input object, or union
        type, or the field is present, but is a generic field common to
        all objects, such as "__typename".
        """
        raise NotImplementedError('Subclasses must implement')

    def _type_name(self):
        return self.name

    def _description(self):
        return self.description
