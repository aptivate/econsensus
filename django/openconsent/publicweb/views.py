# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic import list_detail
from django.http import HttpResponse
import logging

import unicodecsv

from models import Decision
from publicweb.forms import DecisionForm, FeedbackForm
from django.db.models.aggregates import Count

#TODO: Exporting as csv is a generic function that can be required of any database.
#Therefore it should be its own app.
#This looks like it's already been done... see https://github.com/joshourisman/django-tablib
@login_required
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

    opts = Decision._meta #@UndefinedVariable
    field_names = set([field.name for field in opts.fields])

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

    writer = unicodecsv.writer(response)
    # example of using writer.writerow: writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(list(field_names))
    for obj in Decision.objects.all():
        writer.writerow([unicode(getattr(obj, field)).encode("utf-8","replace") for field in field_names])
    return response

@login_required        
def decision_detail(request, object_id, *args, **kwargs):
    decision = get_object_or_404(Decision, pk=object_id)    
    extra_context = { 'tab': decision.status }
    # Show the detail page
    return list_detail.object_detail(
        request,
        queryset = Decision.objects.all(),
        object_id = object_id,
        extra_context = extra_context,
        *args,
        **kwargs
    )

@login_required        
def object_list_by_status(request, status):
    extra_context = { 'tab': status }
    #need to check template exists...
    template_name = status + '_list.html'
    
    if 'sort' in request.GET:
        order = str(request.GET['sort'])
        extra_context['sort'] = order
    else:
        order = '-id'
        extra_context['sort'] = "id"
        
    if order == 'watchers':
        full_queryset = Decision.objects.order_by_count('watchers')
    elif order == 'feedback':
        full_queryset = Decision.objects.order_by_count('feedback')
    elif order == 'decided_date':
        full_queryset = Decision.objects.order_null_last('decided_date')
    elif order == 'effective_date':
        full_queryset = Decision.objects.order_null_last('effective_date')
    elif order == 'review_date':
        full_queryset = Decision.objects.order_null_last('review_date')
    elif order == 'expiry_date':
        full_queryset = Decision.objects.order_null_last('expiry_date')
    elif order == 'deadline':
        full_queryset = Decision.objects.order_null_last('deadline')
    elif order == 'archived_date':
        full_queryset = Decision.objects.order_null_last('archived_date')
    else:
        full_queryset = Decision.objects.order_by(order)
        
    queryset = full_queryset.filter(status=status)
    
    return list_detail.object_list(
        request,
        queryset,
        template_name = template_name,
        extra_context = extra_context
        )

@login_required
def create_decision(request, status, template_name):
    extra_context = { 'tab': status }
    
    decision = Decision(status=status)
    decision.author = request.user
    
    if request.method == "POST":
        return _process_post_and_redirect(request, decision, template_name)

    form = DecisionForm(instance=decision)    
    data = dict(form=form,extra_context=extra_context)
    context = RequestContext(request, data)
    return render_to_response(template_name, context)

@login_required
def update_decision(request, object_id, template_name):
    decision = get_object_or_404(Decision, id = object_id)
    extra_context = { 'tab': decision.status }

    if request.method == "POST":
        return _process_post_and_redirect(request, decision, template_name)

    form = DecisionForm(instance=decision)    
    data = dict(form=form, extra_context=extra_context)
    context = RequestContext(request, data)
    return render_to_response(template_name, context)

@login_required
def create_feedback(request, model, object_id, template_name):

    decision = get_object_or_404(model, id = object_id)
    
    if request.method == "POST":
        if request.POST.get('submit', None) == "Cancel":
            return HttpResponseRedirect(reverse('publicweb_item_detail', args=[unicode(decision.id)]))
        else:
            form = FeedbackForm(request.POST)
            if form.is_valid():
                feedback = form.save(commit=False)
                feedback.decision = decision
                feedback.author = request.user
                feedback.save()
                return HttpResponseRedirect(reverse('publicweb_item_detail', args=[unicode(decision.id)]))
        
        data = dict(form=form)
        context = RequestContext(request, data)
        return render_to_response(template_name, context)

    else:
        form = FeedbackForm()
        
    data = dict(form=form)
    context = RequestContext(request, data)
    return render_to_response(template_name, context)

@login_required
def update_feedback(request, model, object_id, template_name):

    feedback = get_object_or_404(model, id = object_id)
    extra_context = { 'tab': feedback.decision.status }

    if request.method == "POST":
        if request.POST.get('submit', None) == "Cancel":
            return HttpResponseRedirect(feedback.get_parent_url())
        else:
            form = FeedbackForm(request.POST, instance=feedback)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(feedback.get_parent_url())
        
        data = dict(form=form,extra_context=extra_context)
        context = RequestContext(request, data)
        return render_to_response(template_name, context)

    else:
        form = FeedbackForm(instance=feedback)
        
    data = dict(form=form,extra_context=extra_context)
    context = RequestContext(request, data)
    return render_to_response(template_name, context)

def _process_post_and_redirect(request, decision, template_name):
    extra_context={'tab': decision.status}
    if request.POST.get('submit', None) == "Cancel":
        return HttpResponseRedirect(reverse(object_list_by_status, args=[decision.status]))
    else:
        form = DecisionForm(request.POST, instance=decision)
        
        if form.is_valid():
            decision = form.save()
            if form.cleaned_data['watch']:
                decision.add_watcher(request.user)
            else:
                decision.remove_watcher(request.user)
            return HttpResponseRedirect(reverse(object_list_by_status, args=[decision.status]))
        
        data = dict(form=form, extra_context=extra_context)
        context = RequestContext(request, data)
        return render_to_response(template_name, context)   
