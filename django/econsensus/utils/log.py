# Filters to be used by python logging.
# Required because we're using Django 1.3
# Remove on move to Django 1.4 and use django.utils.log.RequireDebugFalse

from logging import Filter
from django.conf import settings

class RequireDebugFalse(Filter):
    def filter(self, record):
        return not settings.DEBUG

class RequireDebugTrue(Filter):
    def filter(self, record):
        return settings.DEBUG
