import django_tables
from django.utils.translation import ugettext_lazy as _

class DecisionTable(django_tables.ModelTable):
    id = django_tables.Column(verbose_name=_('ID'))
    short_name = django_tables.Column(verbose_name=_('Decision'))
    status_text = django_tables.Column(verbose_name=_('Status'))
    unresolvedfeedback = django_tables.Column(verbose_name=_('Feedback'))
    decided_date = django_tables.Column(verbose_name=_('Decided'))
    review_date = django_tables.Column(verbose_name=_('Review'))
    expiry_date = django_tables.Column(verbose_name=_('Expires'))

