# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from models import Decision
from forms import DecisionForm, FeedbackFormSet
from decision_table import DecisionTable

import unicodecsv
from django.http import HttpResponse
from publicweb.proposal_table import ProposalTable
from publicweb.forms import SortForm
from publicweb.forms import FilterForm
    
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

    def fieldOutput(obj,field):
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
        writer.writerow([unicode(fieldOutput(obj,field)).encode("utf-8","replace") for field in field_names])
    return response

@login_required        
def decision_list(request):  
    queryset = Decision.objects.filter(status=Decision.CONSENSUS_STATUS)
            
    decisions = DecisionTable(list(queryset), order_by=request.GET.get('sort'))
        
    return render_to_response('decision_list.html',
        RequestContext(request, dict(decisions=decisions)))

@login_required        
def proposal_list(request):
    sort_form = SortForm(request.GET)
    if sort_form.is_valid() and sort_form.cleaned_data['sort']:
        queryset = Decision.objects.filter(status=Decision.PROPOSAL_STATUS).order_by(str(sort_form.cleaned_data['sort']))
    else:
        queryset = Decision.objects.filter(status=Decision.PROPOSAL_STATUS)

    proposals = ProposalTable(list(queryset), order_by=request.GET.get('sort'))
        
    return render_to_response('proposal_list.html',
        RequestContext(request, dict(proposals=proposals, sort_form=sort_form)))

@login_required        
def archived_list(request):
    queryset = Decision.objects.filter(status=Decision.ARCHIVED_STATUS)      
    proposals = ProposalTable(list(queryset), order_by=request.GET.get('sort'))
        
    return render_to_response('archived_list.html',
        RequestContext(request, dict(objects=proposals)))

@login_required
def modify_decision(request, decision_id = None):
    if decision_id is None:
        decision = None
    else:
        decision = get_object_or_404(Decision, id = decision_id)
    
    if request.method == "POST":
        if request.POST.get('submit', None) == "Cancel":
            return HttpResponseRedirect(reverse(decision_list))
        
        else:
            decision_form = DecisionForm(data=request.POST, 
                                         instance=decision)
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
                    return HttpResponseRedirect(reverse(decision_list))

    else:
        feedback_formset = FeedbackFormSet(instance=decision)
        decision_form = DecisionForm(instance=decision)
        
    return render_to_response('decision_form.html',
        RequestContext(request,
            dict(decision_form=decision_form, feedback_formset=feedback_formset)))

@login_required
def add_decision(request):
    return modify_decision(request)

@login_required    
def edit_decision(request, decision_id):
    return modify_decision(request, decision_id)