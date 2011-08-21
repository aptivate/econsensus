# Create your views here.

from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from models import Decision
from forms import DecisionForm, FeedbackFormSet, FilterForm
from publicweb.decision_table import DecisionTable

import unicodecsv
from django.http import HttpResponse

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

	opts = Decision._meta
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
    
    #build status tuple
    status_code_list = []
    for this_status in Decision.STATUS_CHOICES:
        status_code_list.append(this_status[0])
    status_code_tuple = tuple(status_code_list)
    
    status = request.GET.get('status', None)
    if status is not None and int(status) in status_code_tuple:
        filter_form = FilterForm(request.GET)
        objects = Decision.objects.filter(status=status)
    else:
        filter_form = FilterForm()
        objects = Decision.objects.all()
        
    decisions = DecisionTable(objects, order_by=request.GET.get('sort'))
    return render_to_response('decision_list.html',
        RequestContext(request, dict(decisions=decisions,filter_form=filter_form)))

@login_required
def add_decision(request):
    
    if request.POST:
        decision_form = DecisionForm(request.POST)
        feedback_formset = FeedbackFormSet()
        if decision_form.is_valid():
            decision = decision_form.save(commit=False)
            feedback_formset = FeedbackFormSet(request.POST, instance=decision)
            if feedback_formset.is_valid():
                decision_form.save()
                feedback_formset.save()
                return HttpResponseRedirect(reverse(decision_list))
        
    else:
        feedback_formset = FeedbackFormSet()
        decision_form = DecisionForm()
        
    return render_to_response('decision_form.html',
        RequestContext(request,
            dict(decision_form=decision_form, feedback_formset=feedback_formset)))

@login_required    
def edit_decision(request, decision_id):
    decision = get_object_or_404(Decision, id = decision_id)
    decision_form = DecisionForm(instance=decision)
    feedback_formset = FeedbackFormSet(instance=decision)
    
    if request.method == 'POST':
        decision_form = DecisionForm(request.POST, instance=decision)
                
        if decision_form.is_valid():
            decision = decision_form.save(commit=False)
            feedback_formset = FeedbackFormSet(request.POST,instance=decision)
            if feedback_formset.is_valid():
                decision_form.save()
                feedback_formset.save()
                return HttpResponseRedirect(reverse(decision_list))
        
    return render_to_response('decision_form.html',
        RequestContext(request,
                       dict(decision = decision,
                            decision_form=decision_form,
                            feedback_formset=feedback_formset)))    
