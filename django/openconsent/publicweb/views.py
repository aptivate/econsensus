# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import list_detail
from django.http import HttpResponse

import unicodecsv

from models import Decision
from publicweb.forms import DecisionForm, FeedbackForm, SortForm

#TODO: Remove references to feedback...
def process_post_and_redirect(request, decision, template_name):
    if request.POST.get('submit', None) == "Cancel":
        return_page = unicode(decision.status_text())            
        return HttpResponseRedirect(reverse(object_list_by_status, args=[return_page]))
    else:
        form = DecisionForm(request.POST, instance=decision)
        
        if form.is_valid():
            decision = form.save(commit=False)
            decision.author = request.user
            decision.save()
            if form.cleaned_data['watch']:
                decision.add_watcher(request.user)
            else:
                decision.remove_watcher(request.user)
            return_page = unicode(decision.status_text())
            return HttpResponseRedirect(reverse(object_list_by_status, args=[return_page]))
        
        data = dict(form=form)
        context = RequestContext(request, data)
        return render_to_response(template_name, context)

#TODO: Exporting as csv is a generic function that can be required of any database.
#Therefore it should be its own app.
#This looks like it's already been done... see https://github.com/joshourisman/django-tablib
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

    def fieldOutput(obj, field):
        '''Looks up the status_text() for status, otherwise just returns the getattr for the field'''
        if field == 'status':
            return obj.status_text()
        else:
            return getattr(obj, field)

    opts = Decision._meta #@UndefinedVariable
    field_names = set([field.name for field in opts.fields])

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

    writer = unicodecsv.writer(response)
    # example of using writer.writerow: writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(list(field_names))
    for obj in Decision.objects.all():
        writer.writerow([unicode(fieldOutput(obj, field)).encode("utf-8","replace") for field in field_names])
    return response

#Codes are used to dodge translation in urls.
#Need to think of a better way to do this...
context_codes = { 'proposal' : Decision.PROPOSAL_STATUS,
             'decision' : Decision.DECISION_STATUS,
             'archived' : Decision.ARCHIVED_STATUS,
             }

@login_required        
def object_list_by_status(request, status_text):
    extra_context = { 'status_text': status_text,
                     'sort_form': SortForm(request.GET) }
    status = context_codes[status_text]
    #need to check template exists...
    template_name = status_text + '_list.html'
    
    if 'sort' in request.GET:
        order = str(request.GET['sort'])
    else:
        order = 'id'
    queryset = Decision.objects.order_by(order).filter(status=status)
    extra_context['sort'] = order
    
    return list_detail.object_list(
        request,
        queryset,
        template_name = template_name,
        extra_context = extra_context
        )

@login_required
def create_decision(request, status_id, template_name):
    
    decision = Decision(status=int(status_id))
    
    if request.method == "POST":
        return process_post_and_redirect(request, decision, template_name)

    form = DecisionForm(instance=decision)    
    data = dict(form=form)
    context = RequestContext(request, data)
    return render_to_response(template_name, context)

def update_decision(request, object_id, template_name):
    decision = get_object_or_404(Decision, id = object_id)

    if request.method == "POST":
        return process_post_and_redirect(request, decision, template_name)

    form = DecisionForm(instance=decision)    
    data = dict(form=form)
    context = RequestContext(request, data)
    return render_to_response(template_name, context)

def create_feedback(request, model, object_id, template_name):

    decision = get_object_or_404(model, id = object_id)
            
    if request.method == "POST":
        if request.POST.get('submit', None) == "Cancel":
            return_page = unicode(decision.id)            
            return HttpResponseRedirect(reverse('publicweb_item_detail', args=[return_page]))
        else:
            form = FeedbackForm(request.POST)
            if form.is_valid():
                feedback = form.save(commit=False)
                feedback.decision = decision
                feedback.save()
                return_page = unicode(decision.id)
                return HttpResponseRedirect(reverse('publicweb_item_detail', args=[return_page]))
        
        data = dict(form=form)
        context = RequestContext(request, data)
        return render_to_response(template_name, context)

    else:
        form = FeedbackForm()
        
    data = dict(form=form)
    context = RequestContext(request, data)
    return render_to_response(template_name, context)

def update_feedback(request, model, object_id, template_name):

    feedback = get_object_or_404(model, id = object_id)

    if request.method == "POST":
        if request.POST.get('submit', None) == "Cancel":
            return HttpResponseRedirect(feedback.get_parent_url())
        else:
            form = FeedbackForm(request.POST, instance=feedback)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(feedback.get_parent_url())
        
        data = dict(form=form)
        context = RequestContext(request, data)
        return render_to_response(template_name, context)

    else:
        form = FeedbackForm(instance=feedback)
        
    data = dict(form=form)
    context = RequestContext(request, data)
    return render_to_response(template_name, context)


def _filter(queryset, status):    
    return queryset.filter(status=status)
        
