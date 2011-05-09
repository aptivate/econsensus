# Create your views here.

import logging

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Decision

def home_page(request):
    return render_to_response('home_page.html',
        RequestContext(request,
            dict(decisions=list(Decision.objects.all()))))