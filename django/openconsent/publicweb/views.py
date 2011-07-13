# Create your views here.

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from models import Decision
from forms import DecisionForm, ConcernFormSet
from publicweb.decision_table import DecisionTable

@login_required        
def decision_list(request):
    decisions = DecisionTable(Decision.objects.all(),
        order_by=request.GET.get('sort'))
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