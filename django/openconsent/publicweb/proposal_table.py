import django_tables2 as tables
from django.utils.translation import ugettext_lazy as _

#tables seem a bit useless now that we are using divs in our html page.
#Consider ditching.
#Also note the fudge name change from decided_date to deadline.

class ProposalTable(tables.Table):
    id = tables.Column(verbose_name=_('ID'))
    description_excerpt = tables.Column(verbose_name=_('Excerpt'))
    unresolvedfeedback = tables.Column(verbose_name=_('Activity'))
    decided_date = tables.Column(verbose_name=_('Deadline'))
