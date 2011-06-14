# Create your views here.

import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from models import Decision, Concern
from forms import DecisionForm, ConcernFormSet

import django_tables
  
class DecisionTable(django_tables.ModelTable):
    id = django_tables.Column(sortable=False, visible=False)
    short_name = django_tables.Column(verbose_name='Decision')
    unresolvedconcerns = django_tables.Column(verbose_name='Unresolved Concerns')
    decided_date = django_tables.Column()
    review_date = django_tables.Column()
    expiry_date = django_tables.Column()
        
def decision_list(request):
    decisions = DecisionTable(Decision.objects.all(),
        order_by=request.GET.get('sort'))
    return render_to_response('decision_list.html',
        RequestContext(request, dict(decisions=decisions,)))

@login_required
def decision_add_page(request):
    
    if request.POST:
        decision_form = DecisionForm(request.POST)
        if decision_form.is_valid():
            decision = decision_form.save(commit=False)
            concern_form = ConcernFormSet(request.POST, instance=decision)
            if concern_form.is_valid():
                decision_form.save()
                concern_form.save()
                return HttpResponseRedirect(reverse(decision_list))
        
        return HttpResponseRedirect(reverse(decision_add_page))

    else:
        concern_form = ConcernFormSet()
        decision_form = DecisionForm()
        
    return render_to_response('decision_add.html',
        RequestContext(request,
            dict(decision_form=decision_form, concern_form=concern_form)))
    
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

        return HttpResponseRedirect(reverse(decision_add_page))
        
    return render_to_response('decision_add.html',
        RequestContext(request,
                       dict(decision = decision,
                            decision_form=decision_form,
                            concern_form=concern_form)))

    