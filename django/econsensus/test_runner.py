from django.core.exceptions import ImproperlyConfigured
from django.test.simple import DjangoTestSuiteRunner, \
    reorder_suite, build_suite
from django.test.testcases import TestCase
from django.db.models import get_apps
from django.utils.importlib import import_module

try:
    from django.utils import unittest
except ImportError:
    try:
        import unittest2 as unittest
    except ImportError:
        raise ImproperlyConfigured("Couldn't import unittest2 default "
                                   "test loader. Please use Django >= 1.3 "
                                   "or install the unittest2 library.")


class DiscoveryRunner(DjangoTestSuiteRunner):
    """
    A test suite runner combining default django behavior with the smart
    test discovery of djano-discover-runner. With snippets taken from carljm
    https://gist.github.com/carljm/1450104 and
    https://github.com/jezdez/django-discover-runner

    Running './manage.py test' will run all tests including those "smart found"
    in applications (default django behavior plus default django-test-runner
    behavior).

    Using './manage.py test projectapps' will run all the tests in your source
    folder but not all installed apps (the default behavior of
    django-discover-runner)

    Specifying an app name like './manage.py app', will just run the tests
    "smart found" for that app.
    ** You cannot specify multiple apps to run tests from (just one or all). **

    Or you can supply a series of test files / test names with dotted names
    e.g. ./manage.py app1.tests.test_file app2.tests.file.TestClass.test_method
    """

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = None
        pattern = '*_test.py'

        # Do default test loading if no test labels specfied
        if not test_labels:
            suite = unittest.TestSuite()
            for app in get_apps():
                suite.addTest(build_suite(app))

            # Then intelligent test find from top directory
            suite.addTest(unittest.defaultTestLoader.discover('.',
                                                              pattern=pattern))

        # If 'projectapps' in test_labels then find only the tests in my
        # project, but find all of them
        if 'projectapps' in test_labels:
            suite = unittest.TestSuite()
            suite.addTest(unittest.defaultTestLoader.discover('.',
                                                              pattern=pattern))

        # Else can only handle a single project name or a series of tests
        elif test_labels:
            root = '.'
            # Loads tests from dotted tests names
            suite = unittest.defaultTestLoader.loadTestsFromNames(test_labels)
            # if single named module has no tests, do discovery within it
            if not suite.countTestCases() and len(test_labels) == 1:
                suite = None
                root = import_module(test_labels[0]).__path__[0]
                suite = unittest.defaultTestLoader.discover(root,
                                                            pattern=pattern)

        # Default DjangoTestSuiteRunner behavior
        if extra_tests:
            for test in extra_tests:
                suite.addTest(test)

        return reorder_suite(suite, (TestCase,))