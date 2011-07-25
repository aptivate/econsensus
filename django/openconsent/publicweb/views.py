# Create your views here.

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from models import Decision
from forms import DecisionForm, FeedbackFormSet, FilterForm
from publicweb.decision_table import DecisionTable

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
        feedback_form = FeedbackFormSet()
        if decision_form.is_valid():
            decision = decision_form.save(commit=False)
            feedback_form = FeedbackFormSet(request.POST, instance=decision)
            if feedback_form.is_valid():
                decision_form.save()
                feedback_form.save()
                return HttpResponseRedirect(reverse(decision_list))
        
    else:
        feedback_form = FeedbackFormSet()
        decision_form = DecisionForm()
        
    return render_to_response('decision_form.html',
        RequestContext(request,
            dict(decision_form=decision_form, feedback_form=feedback_form)))

@login_required    
def edit_decision(request, decision_id):
    decision = get_object_or_404(Decision, id = decision_id)
    decision_form = DecisionForm(instance=decision)
    feedback_form = FeedbackFormSet(instance=decision)
    
    if request.method == 'POST':
        decision_form = DecisionForm(request.POST, instance=decision)
                
        if decision_form.is_valid():
            decision = decision_form.save(commit=False)
            feedback_form = FeedbackFormSet(request.POST,instance=decision)
            if feedback_form.is_valid():
                decision_form.save()
                feedback_form.save()
                return HttpResponseRedirect(reverse(decision_list))
        
    return render_to_response('decision_form.html',
        RequestContext(request,
                       dict(decision = decision,
                            decision_form=decision_form,
                            feedback_form=feedback_form)))    