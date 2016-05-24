import importlib
import inspect


class GraphQlClassDescriptor(object):
    """Identifies a Python class.

    The use of a GraphQlClassDescriptor, as opposed to a direct
    reference to the class, enables us to import the class on demand.
    Two GraphQlClassDescriptors are equal (as in ==, !=, and "hash") if
    they refer to the same class.

    Public attributes:

    basestring class_name - The name of the class.
    basestring module_name - The name of the module containing the
        class.
    """

    def __init__(self, module_name, class_name):
        self.module_name = module_name
        self.class_name = class_name

    @staticmethod
    def create_from_class(cls):
        """Return a GraphQlClassDescriptor for the specified class.

        type cls - The class.
        return GraphQlClassDescriptor - The class descriptor.
        """
        return GraphQlClassDescriptor(
            inspect.getmodule(cls).__name__, cls.__name__)

    def load_class(self):
        """Return the class that this identifies."""
        module = importlib.import_module(self.module_name)
        return getattr(module, self.class_name)

    def __eq__(self, other):
        return (
            isinstance(other, GraphQlClassDescriptor) and
            self.module_name == other.module_name and
            self.class_name == other.class_name)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.module_name, self.class_name))
