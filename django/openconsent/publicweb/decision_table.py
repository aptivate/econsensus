import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _

class DecisionTable(tables.Table):
    id = tables.Column(verbose_name=_('ID'))
    short_name = tables.Column(verbose_name=_('Decision'))
    status_text = tables.Column(verbose_name=_('Status'))
    unresolvedfeedback = tables.Column(verbose_name=_('Feedback'))
    decided_date = tables.Column(verbose_name=_('Decided'))
    review_date = tables.Column(verbose_name=_('Review'))
    expiry_date = tables.Column(verbose_name=_('Expires'))

