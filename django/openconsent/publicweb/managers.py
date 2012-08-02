#Model managers for models
from django.db import models
from django.db.models.aggregates import Count

class DecisionManager(models.Manager):
    def order_by_count(self, field):
        return super(DecisionManager, self).get_query_set()\
            .annotate(count=Count(field))\
            .order_by('-count')

    def order_null_last(self, field):
        return super(DecisionManager, self).get_query_set()\
            .extra(select={'has_field': "CASE WHEN " + field + " IS NULL THEN 1 ELSE 0 END"})\
            .order_by('has_field', field)
