# Create your views here.

import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from models import Decision, DecisionList
from forms import DecisionForm

import django_tables
  
class DecisionTable(django_tables.ModelTable):
    id = django_tables.Column(sortable=False, visible=False)
    short_name = django_tables.Column(verbose_name='Decision')
    concerns_yesno = django_tables.Column(verbose_name='Any concerns')
    decided_date = django_tables.Column()
    review_date = django_tables.Column()
    expiry_date = django_tables.Column()
        
def decision_list(request, decisionlist_id):
    
    decisionlist = get_object_or_404(DecisionList, pk=decisionlist_id)
    
    decisions = DecisionTable(decisionlist.decision_set.all(),
        order_by=request.GET.get('sort'))
    return render_to_response('decision_list.html',
        RequestContext(request, dict(decisions=decisions,decisionlist=decisionlist)))

def decision_add_page(request):
    if request.POST:
        decision_form = DecisionForm(request.POST)
        if decision_form.is_valid():
            decision = decision_form.save()
            return HttpResponseRedirect(reverse(decision_list,
                                                args=[decision.decision_list.id]))
    else:
        decision_form = DecisionForm()
        
    return render_to_response('decision_add.html',
        RequestContext(request,
            dict(decision_form=decision_form)))
    

def decision_view_page(request, decision_id):
    decision = Decision.objects.get(id = decision_id)
    decision_form = DecisionForm(instance=decision)
    
    if request.method == 'POST':
        decision_form = DecisionForm(request.POST, instance=decision)
        if decision_form.is_valid():
            decision_form.save()
            return HttpResponseRedirect(reverse(decision_list,
                                                args=[decision.decision_list.id]))
        
    return render_to_response('decision_add.html',
        RequestContext(request, dict(decision_form=decision_form)))

def decision_lists(request):
    decision_lists = DecisionList.objects.all()
     
    return render_to_response('decision_lists.html',
        RequestContext(request, dict(decision_lists=decision_lists)))
