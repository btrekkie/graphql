import importlib
import inspect


class GraphQlFuncDescriptor(object):
    """Identifies a Python static method or global function.

    The use of a GraphQlFuncDescriptor, as opposed to a direct reference
    to the function, enables us to import the function on demand.  Two
    GraphQlFuncDescriptors are equal (as in == and !=) if they refer to
    the same function.

    <T> - The type of the function.

    Public attributes:

    basestring class_name - The name of the class containing the method,
        or None if it is not a static method.
    basestring func_name - The name of the method or function.
    basestring module_name - The name of the Python module containing
        the method or function.
    """

    def __init__(self, module_name, class_name, func_name):
        self.module_name = module_name
        self.class_name = class_name
        self.func_name = func_name

    @staticmethod
    def create_from_func(func):
        """Return a GraphQlFuncDescriptor for a static method or function.

        function func - The static method or function.
        return GraphQlFuncDescriptor - The function descriptor.
        """
        cls = getattr(func, 'im_class', None)
        if cls is None:
            class_name = None
        else:
            class_name = cls.__name__
        return GraphQlFuncDescriptor(
            inspect.getmodule(func).__name__, class_name, func.__name__)

    def load_func(self):
        """Return the static method or function that this identifies."""
        module = importlib.import_module(self.module_name)
        if self.class_name is None:
            return getattr(module, self.func_name)
        else:
            cls = getattr(module, self.class_name)
            return getattr(cls, self.func_name)

    def __eq__(self, other):
        return (
            isinstance(other, GraphQlFuncDescriptor) and
            self.module_name == other.module_name and
            self.class_name == other.class_name and
            self.func_name == other.func_name)

    def __ne__(self, other):
        return not (self == other)
