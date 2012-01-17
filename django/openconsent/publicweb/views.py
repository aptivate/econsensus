# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import list_detail
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

import unicodecsv

from models import Decision, Feedback
from forms import ProposalForm, DecisionForm, ArchivedForm, FeedbackFormSet
from forms import SortForm

def get_form(request, decision):
    if request.method == 'POST':
        data = request.POST
    else:
        data = None
        
    if decision.status == Decision.ARCHIVED_STATUS:
        return ArchivedForm(data=data, instance=decision)
    elif decision.status == Decision.DECISION_STATUS:
        return DecisionForm(data=data, instance=decision)
    else:
        return ProposalForm(data=data, instance=decision)
        
def process_post_and_redirect(request, decision):
    if request.POST.get('submit', None) == "Cancel":
        return_page = unicode(decision.status_text())            
        return HttpResponseRedirect(reverse(listing, args=[return_page]))
    else:
        decision_form = get_form(request, decision)
            
        feedback_formset = FeedbackFormSet(data=request.POST, 
                                           instance=decision)

        if decision_form.is_valid():
            decision = decision_form.save(commit=False)
            feedback_formset = FeedbackFormSet(request.POST, 
                                               instance=decision)
            if feedback_formset.is_valid():
                decision.save(request.user)
                if decision_form.cleaned_data['watch']:
                    decision.add_watcher(request.user)
                else:
                    decision.remove_watcher(request.user)
                feedback_formset.save()
                
                return_page = unicode(decision.status_text())
                return HttpResponseRedirect(reverse(listing, args=[return_page]))
        
        data = dict(decision_form=decision_form, feedback_formset=feedback_formset)
        context = RequestContext(request, data)
        return render_to_response('decision_edit.html', context)


#TODO: Exporting as csv is a generic function that can be required of any database.
#Therefore it should be its own app.
#This looks like it's already been done... see https://github.com/joshourisman/django-tablib
def export_csv(request):
    ''' Create the HttpResponse object with the appropriate CSV header and corresponding CSV data from Decision.
	Expected input: request (not quite sure what this is!)
	Expected output: http containing MIME info followed by the data itself as CSV.
	>>> res = export_csv(1000)
	>>> res.status_code
	200
	>>> res['Content-Disposition']
	'attachment; filename=publicweb_decision.csv'
	>>> res['Content-Type']
	'text/csv'
	>>> len(res.content)>0
	True
	'''

    def fieldOutput(obj, field):
        '''Looks up the status_text() for status, otherwise just returns the getattr for the field'''
        if field == 'status':
            return obj.status_text()
        else:
            return getattr(obj, field)

    opts = Decision._meta #@UndefinedVariable
    field_names = set([field.name for field in opts.fields])

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

    writer = unicodecsv.writer(response)
    # example of using writer.writerow: writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(list(field_names))
    for obj in Decision.objects.all():
        writer.writerow([unicode(fieldOutput(obj, field)).encode("utf-8","replace") for field in field_names])
    return response

# TODO: a better way to handle all these list views is to create a single view for listing items
# that view will use a search function that takes a 'filter' parameter and an 'order_by' parameter and gives an ordered queryset back.
# The list view will use a single template but will pass a parameter as extra context to individualise the page

proposal_context = {'page_title' : _("Current Active Proposals"), # pylint: disable=E1102
                     'class' : 'proposal',
                     'columns': ('id', 'excerpt', 'feedbackcount', 'deadline')}

decision_context = {'page_title' : _("Decisions Made"), # pylint: disable=E1102
                     'class' : 'decision',
                     'columns': ('id', 'excerpt', 'decided_date', 'review_date')}

archived_context = {'page_title' : _("Archived Decisions"), # pylint: disable=E1102
                     'class' : 'archived',
                     'columns': ('id', 'excerpt', 'created_date', 'archived_date')}

context_list = { 'proposal' : proposal_context,
             'decision' : decision_context,
             'archived' : archived_context,
             }

#Codes are used to dodge translation in urls.
#Need to think of a better way to do this...
context_codes = { 'proposal' : Decision.PROPOSAL_STATUS,
             'decision' : Decision.DECISION_STATUS,
             'archived' : Decision.ARCHIVED_STATUS,
             }

@login_required        
def listing(request, status):
    extra_context = context_list[status]
    extra_context['status'] = status
    extra_context['sort_form'] = SortForm(request.GET)
    status_code = context_codes[status]
    
    if 'sort' in request.GET:
        order = str(request.GET['sort'])
        queryset = _filter(Decision.objects.order_by(order), status_code)
    else:
        queryset = _filter(Decision.objects.order_by('id'), status_code)
        order = 'id'
    
    extra_context['sort'] = order
    
    return list_detail.object_list(
        request,
        queryset,
        template_name = 'item_list.html',
        extra_context = extra_context
        )

@login_required
def modify(request, decision_id):

    decision = get_object_or_404(Decision, id = decision_id)
    
    if request.method == "POST":
        return process_post_and_redirect(request, decision)
    else:
        feedback_formset = FeedbackFormSet(instance=decision)
        decision_form = get_form(request, decision)
        
    data = dict(decision_form=decision_form, feedback_formset=feedback_formset)
    context = RequestContext(request, data)
    return render_to_response('decision_edit.html', context)

@login_required
def new(request, status_id):
    
    decision = Decision(status=int(status_id))
        
    if request.method == "POST":
        return process_post_and_redirect(request, decision)
    else:
        feedback_formset = FeedbackFormSet(instance=decision)
        decision_form = get_form(request, decision)
        
    data = dict(decision_form=decision_form, feedback_formset=feedback_formset)
    context = RequestContext(request, data)
    return render_to_response('decision_edit.html', context)

@login_required
def inline_modify_decision(request, decision_id, template_name="decision_detail.html"):
    if decision_id is None:
        decision = None
    else:
        decision = get_object_or_404(Decision, id = decision_id)

    if request.method == "POST":
        if request.POST.get('submit', None) == "Cancel":
            return HttpResponseRedirect(reverse("view_decision", args=[decision_id]))

        else:
            decision_form = DecisionForm(data=request.POST, 
                                         instance=decision)
            if decision_form.is_valid():
                decision = decision_form.save(commit=False)
                decision.save(request.user)
                return HttpResponseRedirect(reverse("view_decision", args=[decision_id]))
    else:
        decision_form = DecisionForm(instance=decision)

    return render_to_response(template_name,
        RequestContext(request,
            dict(object=decision, decision_form=decision_form, show_form=True)))

@login_required
def view_decision(request, decision_id, template_name="decision_detail.html"):
    decision = get_object_or_404(Decision, id = decision_id)
    
    return render_to_response(template_name,
                              {'object':decision},
                              context_instance=RequestContext(request))

def _filter(queryset, status):    
    return queryset.filter(status=status)
        
