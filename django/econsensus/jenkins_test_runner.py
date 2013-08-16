from test_runner import DiscoveryRunner
from django_selenium.jenkins_runner import JenkinsTestRunner


class DiscoveryCITestSuiteRunner(DiscoveryRunner, JenkinsTestRunner):
    pass
