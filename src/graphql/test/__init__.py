"""Runs all of the tests in the "graphql" module."""

if __name__ == '__main__':
    import unittest

    from graphql.document.test import *
    from graphql.executor.test import *
    from graphql.scalar_descriptors.lax.test import *
    from graphql.scalar_descriptors.strict.test import *
    from graphql.schema.test import *

    unittest.main()
