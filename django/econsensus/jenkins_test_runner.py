from test_runner import DiscoveryRunner
from django_jenkins.runner import CITestSuiteRunner


class DiscoveryCITestSuiteRunner(DiscoveryRunner, CITestSuiteRunner):
    pass
