# Create your views here.

import logging

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Decision
from forms import DecisionForm

def home_page(request):
    return render_to_response('home_page.html',
        RequestContext(request,
            dict(decisions=list(Decision.objects.all()))))
            
def decision_add_page(request):
    return render_to_response('decision_add.html',
        RequestContext(request,
            dict(decision_form=DecisionForm())))
    
def decision_view_page(request):
    pass
    