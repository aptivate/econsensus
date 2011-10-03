import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _

class DecisionTable(tables.Table):
    id = tables.Column(verbose_name=_('ID'))
    description_excerpt = tables.Column(verbose_name=_('Excerpt'))
    unresolvedfeedback = tables.Column(verbose_name=_('Feedback'))
    decided_date = tables.Column(verbose_name=_('Decided'))
    review_date = tables.Column(verbose_name=_('Review'))
    expiry_date = tables.Column(verbose_name=_('Expires'))

