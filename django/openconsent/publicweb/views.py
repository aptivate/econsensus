# Create your views here.

import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from models import Decision, Group, Concern
from forms import DecisionForm, GroupForm, ConcernForm

import django_tables
  
class DecisionTable(django_tables.ModelTable):
    id = django_tables.Column(sortable=False, visible=False)
    short_name = django_tables.Column(verbose_name='Decision')
    concerns_yesno = django_tables.Column(verbose_name='Any concerns')
    decided_date = django_tables.Column()
    review_date = django_tables.Column()
    expiry_date = django_tables.Column()
        
def decision_list(request, group_id):
    
    group = get_object_or_404(Group, pk=group_id)
    
    decisions = DecisionTable(group.decision_set.all(),
        order_by=request.GET.get('sort'))
    return render_to_response('decision_list.html',
        RequestContext(request, dict(decisions=decisions,
                                     group=group)))

def decision_add_page(request):
    
    if request.POST:
        decision_form = DecisionForm(request.POST)
        if decision_form.is_valid():
            decision = decision_form.save(commit=False)
            concern_form = ConcernForm(request.POST, instance=decision)
            if concern_form.is_valid():
                decision_form.save()
                concern_form.save()
            return HttpResponseRedirect(reverse(decision_list,
                                                args=[decision.group.id]))
    else:
        concern_form = ConcernForm()
        decision_form = DecisionForm()
        
    return render_to_response('decision_add.html',
        RequestContext(request,
            dict(decision_form=decision_form, concern_form=concern_form)))
    
def decision_view_page(request, decision_id):
    decision = Decision.objects.get(id = decision_id)
    decision_form = DecisionForm(instance=decision)
    concern_form = ConcernForm(instance=decision)
    
    if request.method == 'POST':
        decision_form = DecisionForm(request.POST, instance=decision)
        if decision_form.is_valid():
            decision_form.save()
            return HttpResponseRedirect(reverse(decision_list,
                                                args=[decision.group.id]))
        
    return render_to_response('decision_add.html',
        RequestContext(request, 
                       dict(decision_form=decision_form,
                            concern_form=concern_form)))

def groups(request):
    groups = Group.objects.all()
    
    return render_to_response('groups.html',
        RequestContext(request, dict(groups=groups)))

def group_add(request):
    
    group_form = GroupForm()
    
    if request.method == 'POST':
        group_form = GroupForm(request.POST)
        if group_form.is_valid():
            group_form.save()
            return HttpResponseRedirect(reverse('groups'))
    
    return render_to_response('group_add.html',
        RequestContext(request, dict(group_form=group_form)))
    