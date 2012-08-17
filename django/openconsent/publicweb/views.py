# Create your views here.
from notification import models as notification

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic.base import View, RedirectView
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView

import unicodecsv

from models import Decision, Feedback
from publicweb.forms import DecisionForm, FeedbackForm

class ExportCSV(View):
#TODO: Exporting as csv is a generic function that can be required of any database.
#Therefore it should be its own app.
#This looks like it's already been done... see https://github.com/joshourisman/django-tablib
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ExportCSV, self).dispatch(*args, **kwargs)

    def get(self, request):
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


class DecisionDetail(DetailView):
    model = Decision

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DecisionDetail, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(DecisionDetail, self).get_context_data(**kwargs)
        context['tab'] = self.object.status
        return context

class DecisionList(ListView):
    model = Decision

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DecisionList, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.status = kwargs.get('status', Decision.PROPOSAL_STATUS)
        self.order = request.GET.get('sort', '-id')
        return super(DecisionList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        if self.order == 'feedback':
            qs = Decision.objects.order_by_count('feedback').filter(status=self.status)
        elif self.order == 'decided_date':
            qs = Decision.objects.order_null_last('decided_date').filter(status=self.status)
        elif self.order == 'effective_date':
            qs = Decision.objects.order_null_last('effective_date').filter(status=self.status)
        elif self.order == 'review_date':
            qs = Decision.objects.order_null_last('review_date').filter(status=self.status)
        elif self.order == 'expiry_date':
            qs = Decision.objects.order_null_last('expiry_date').filter(status=self.status)
        elif self.order == 'deadline':
            qs = Decision.objects.order_null_last('deadline').filter(status=self.status)
        elif self.order == 'archived_date':
            qs = Decision.objects.order_null_last('archived_date').filter(status=self.status)
        else:
            qs = Decision.objects.order_by(self.order).filter(status=self.status)
        return qs
    
    def get_context_data(self, *args, **kwargs):
        context = super(DecisionList, self).get_context_data(**kwargs)
        context['tab'] = self.status
        context['sort'] = self.order
        return context

class DecisionCreate(CreateView):
    model = Decision
    form_class = DecisionForm
    status = Decision.PROPOSAL_STATUS
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.status = kwargs.get('status', Decision.PROPOSAL_STATUS)
        return super(DecisionCreate, self).dispatch(*args, **kwargs)

    def get_form(self, form):
        form = super(DecisionCreate, self).get_form(form)
        form.fields['status'].initial = self.status
        return form
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.editor = self.request.user
        form.instance.last_status = 'new'
        return super(DecisionCreate, self).form_valid(form)
    
    def get_context_data(self, *args, **kwargs):
        context = super(DecisionCreate, self).get_context_data(**kwargs)
        context['tab'] = self.status
        return context

    def get_success_url(self, *args, **kwargs):
        return reverse('publicweb_item_list', args=[self.status])

    def post(self, *args, **kwargs):
        if self.request.POST.get('submit', None) == "Cancel":
            return HttpResponseRedirect(self.get_success_url())
        return super(DecisionCreate, self).post(*args, **kwargs)

class DecisionUpdate(UpdateView):
    model = Decision
    form_class = DecisionForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DecisionUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.editor = self.request.user
        form.instance.last_status = self.last_status
        if not form.cleaned_data['watch'] and notification.is_observing(self.object, self.request.user):
            notification.stop_observing(self.object, self.request.user)
        elif form.cleaned_data['watch'] and not notification.is_observing(self.object, self.request.user):
            notification.observe(self.object, self.request.user, 'decision_change')

        return super(DecisionUpdate, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(DecisionUpdate, self).get_context_data(**kwargs)
        context['tab'] = self.object.status
        return context

    def get_success_url(self, *args, **kwargs):
        status = kwargs.get('status', Decision.PROPOSAL_STATUS)
        return reverse('publicweb_item_list', args=[status])

    def post(self, *args, **kwargs):
        if self.request.POST.get('submit', None) == "Cancel":
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.last_status = self.get_object().status
            return super(DecisionUpdate, self).post(*args, **kwargs)

class FeedbackCreate(CreateView):
    model = Feedback
    form_class = FeedbackForm
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeedbackCreate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.decision = Decision.objects.get(pk=self.kwargs['parent_pk'])
        form.instance.last_status = 'new'
        return super(FeedbackCreate, self).form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse('publicweb_item_detail', args=[self.object.decision.pk])
    
    def post(self, *args, **kwargs):
        if self.request.POST.get('submit', None) == "Cancel":
            return HttpResponseRedirect(self.get_success_url())
        return super(FeedbackCreate, self).post(*args, **kwargs)

class FeedbackSnippetCreate(FeedbackCreate):
    def get_success_url(self, *args, **kwargs):
        return reverse('publicweb_feedback_snippet_detail', args=[self.object.pk])

class FeedbackUpdate(UpdateView):
    model = Feedback
    form_class = FeedbackForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeedbackUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, *args, **kwargs):
        if not notification.is_observing(self.object.decision, self.request.user):
            notification.observe(self.object.decision, self.request.user, 'decision_change')
        return super(FeedbackUpdate, self).form_valid(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(FeedbackUpdate, self).get_context_data(**kwargs)
        context['tab'] = self.object.decision.status
        return context

    def get_success_url(self, *args, **kwargs):
        return reverse('publicweb_item_detail', args=[self.object.decision.pk])

@login_required
def update_feedback(request, model, object_id, template_name):

    feedback = get_object_or_404(model, id = object_id)
    if request.method == "POST":
        if request.POST.get('submit', None) == "Cancel":
            return HttpResponseRedirect(feedback.get_parent_url())
        else:
            form = FeedbackForm(request.POST, instance=feedback)
            if form.is_valid():
                form.save()
                if not notification.is_observing(feedback.decision, request.user):
                    notification.observe(feedback.decision, request.user, 'decision_change')
                return HttpResponseRedirect(feedback.get_parent_url())
        
        data = dict(form=form, tab=feedback.decision.status)
        context = RequestContext(request, data)
        return render_to_response(template_name, context)

    else:
        form = FeedbackForm(instance=feedback)
        
    data = dict(form=form, tab=feedback.decision.status)
    context = RequestContext(request, data)
    return render_to_response(template_name, context)
