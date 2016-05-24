import datetime

from graphql import graphql_scalar
from graphql import GraphQlScalarDescriptor


@graphql_scalar('TimeSpan')
class TestGraphQlTimeSpanDescriptor(GraphQlScalarDescriptor):
    """GraphQlScalarDescriptor for the difference between two moments in time.

    The Python representation is a timedelta object, while the scalar
    representation is a number indicating the number of seconds.
    """

    def graphql_to_python(self, value):
        if not isinstance(value, (float, int, long)):
            raise TypeError('Input is not a number')
        return datetime.timedelta(seconds=value)

    def python_to_graphql(self, value):
        if not isinstance(value, datetime.timedelta):
            raise TypeError('Object is not a timedelta')
        return value.total_seconds()
