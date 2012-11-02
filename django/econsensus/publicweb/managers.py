#Model managers for models
from django.db import models
from django.db.models.aggregates import Count


class DecisionManager(models.Manager):

    def order_by_case_insensitive(self, sort_field, sort_order):
        #Django does not yet have case insensitive ordering it is left to db https://code.djangoproject.com/ticket/6498
        return super(DecisionManager, self).get_query_set()\
            .extra(select={'lower': "lower(" + sort_field + ")"}).order_by(sort_order + 'lower')

    def order_by_count(self, sort_field, sort_order):
        return super(DecisionManager, self).get_query_set()\
            .annotate(count=Count(sort_field)).order_by(sort_order + 'count')

    def order_null_last(self, field):
        return super(DecisionManager, self).get_query_set()\
            .extra(select={'has_field': "CASE WHEN " + field + " IS NULL THEN 1 ELSE 0 END"}).order_by('has_field', field)
