# Create your views here.

from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from models import Decision
from forms import DecisionForm, ConcernFormSet
from publicweb.decision_table import DecisionTable

import csv
from django.http import HttpResponse

def export_csv(request):
	''' Create the HttpResponse object with the appropriate CSV header and corresponding CSV data from Decision.
	Expected input: request (not quite sure what this is!)
	Expected output: http containing MIME info followed by the data itself as CSV.
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

	writer = csv.writer(response)
    # example of using writer.writerow: writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
	writer.writerow(list(field_names))
	for obj in Decision.objects.all():
		writer.writerow([unicode(fieldOutput(obj,field)).encode("utf-8","replace") for field in field_names])
	return response

@login_required        
def decision_list(request):
    status = Decision.STATUS_CODES.get(request.GET.get('status'), None)
    
    if status is not None:
        objects = Decision.objects.filter(status=status)
    else:
        objects = Decision.objects.all()
        
    decisions = DecisionTable(objects, order_by=request.GET.get('sort'))
    return render_to_response('decision_list.html',
        RequestContext(request, dict(decisions=decisions,)))

@login_required
def decision_add_page(request):
    
    if request.POST:
        decision_form = DecisionForm(request.POST)
        concern_form = ConcernFormSet()
        if decision_form.is_valid():
            decision = decision_form.save(commit=False)
            concern_form = ConcernFormSet(request.POST, instance=decision)
            if concern_form.is_valid():
                decision_form.save()
                concern_form.save()
                return HttpResponseRedirect(reverse(decision_list))
        
    else:
        concern_form = ConcernFormSet()
        decision_form = DecisionForm()
        
    return render_to_response('decision_add.html',
        RequestContext(request,
            dict(decision_form=decision_form, concern_form=concern_form)))

@login_required    
def decision_view_page(request, decision_id):
    decision = Decision.objects.get(id = decision_id)
    decision_form = DecisionForm(instance=decision)
    concern_form = ConcernFormSet(instance=decision)
    
    if request.method == 'POST':
        decision_form = DecisionForm(request.POST, instance=decision)
                
        if decision_form.is_valid():
            decision = decision_form.save(commit=False)
            concern_form = ConcernFormSet(request.POST,instance=decision)
            if concern_form.is_valid():
                decision_form.save()
                concern_form.save()
                return HttpResponseRedirect(reverse(decision_list))
        
    return render_to_response('decision_add.html',
        RequestContext(request,
                       dict(decision = decision,
                            decision_form=decision_form,
                            concern_form=concern_form)))    
