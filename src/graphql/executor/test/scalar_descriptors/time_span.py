import datetime

from graphql import graphql_enum
from graphql import graphql_field
from graphql import graphql_input_object
from graphql import graphql_object
from graphql import graphql_root_field


@graphql_object('TestTimeSpan')
class TestTimeSpan(object):
    """Provides functionality pertaining to intervals of time."""

    @staticmethod
    @graphql_root_field('testTimeSpan', 'TestTimeSpan!')
    def instance():
        """Return an instance of TestTimeSpan."""
        return TestTimeSpan()

    @staticmethod
    @graphql_enum('TimeUnit')
    def graphql_time_unit_enum():
        """GraphQL enumeration for units of time."""
        return {
            'DAYS': 'days',
            'SECONDS': 'seconds',
            'WEEKS': 'weeks',
        }

    @staticmethod
    @graphql_input_object('Interval')
    def interval_input_type():
        """Describe the input object type for intervals of time.

        return dict<basestring, basestring> - A map from the names of
            the input object fields to their type strings.
        """
        return {
            'number': 'Float!',
            'unit': 'TimeUnit!',
        }

    @graphql_field(
        'timeSum', 'TimeSpan!',
        {'intervals': '[Interval!]', 'times': '[TimeSpan!]'})
    def add_times(self, times=[], intervals=[]):
        """Return the sum of the specified intervals of time.

        list<timedelta> times - The timedeltas to include in the sum.
        list<dict<basestring, object>> - The intervals to include in the
            sum, formatted as suggested by the return value of
            interval_input_type().
        return timedelta - The sum.
        """
        total = datetime.timedelta()
        for time in times:
            total += time
        for interval in intervals:
            if interval['unit'] == 'seconds':
                total += datetime.timedelta(seconds=interval['number'])
            elif interval['unit'] == 'days':
                total += datetime.timedelta(days=interval['number'])
            elif interval['unit'] == 'weeks':
                total += datetime.timedelta(weeks=interval['number'])
        return total
