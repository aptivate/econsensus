# Create your views here.

import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from models import Decision
from forms import DecisionForm

def home_page(request):
    return render_to_response('home_page.html',
        RequestContext(request,
            dict(decisions=Decision.objects.all())))
            
def decision_add_page(request):
    if request.POST:
        decision_form = DecisionForm(request.POST)
        if decision_form.is_valid():
            decision_form.save()
            return HttpResponseRedirect(reverse(home_page))
    else:
        decision_form = DecisionForm()
        
    return render_to_response('decision_add.html',
        RequestContext(request,
            dict(decision_form=decision_form)))
    
def decision_view_page(request):
    pass
    