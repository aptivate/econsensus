import django_tables
from django.utils.translation import ugettext_lazy as _

class DecisionTable(django_tables.ModelTable):
    id = django_tables.Column(sortable=False, visible=False)
    short_name = django_tables.Column(verbose_name=_('Decision'))
    unresolvedconcerns = django_tables.Column(verbose_name=_('Unresolved Concerns'))
    decided_date = django_tables.Column(verbose_name=_('Decided Date'))
    review_date = django_tables.Column(verbose_name=_('Review date'))
    expiry_date = django_tables.Column(verbose_name=_('Expiry Date'))
    status_text = django_tables.Column(verbose_name=_('Status'))


