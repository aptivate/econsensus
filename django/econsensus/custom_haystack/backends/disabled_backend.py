import haystack
from haystack.backends import BaseEngine, BaseSearchBackend, BaseSearchQuery

"""
The "disabled" backend goes further than Haystack's "simple" backend
in not providing any useful search functionality. Configuring Haystack
to use this backend for a connection not only means that search won't
work, but indicates that search has deliberately been disabled - and
hence that search-related UI should be suppressed. (A templatetag library,
search_enabled, can be used to find out whether this is the case.)
"""

class DisabledSearchBackend(BaseSearchBackend):
    def update(self, indexer, iterable, commit=True):
        pass

    def remove(self, obj, commit=True):
        pass

    def clear(self, models=[], commit=True):
        pass

    def search(self, query_string, **kwargs):
        hits = 0
        results = []

        return {
            'results': [],
            'hits': 0,
        }

    def prep_value(self, db_field, value):
        return value

    def more_like_this(self, model_instance, additional_query_string=None,
                       start_offset=0, end_offset=None,
                       limit_to_registered_models=None, result_class=None, **kwargs):
        return {
            'results': [],
            'hits': 0
        }

class DisabledSearchQuery(BaseSearchQuery):
    def build_query(self):
        return '*'

class DisabledEngine(BaseEngine):
    backend = DisabledSearchBackend
    query = DisabledSearchQuery

    def __init__(self, *args, **kwargs):
        super(DisabledEngine, self).__init__(*args, **kwargs)
