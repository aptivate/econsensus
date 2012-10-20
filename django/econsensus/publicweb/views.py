# Create your views here.
from notification import models as notification
from organizations.models import Organization

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import SimpleTemplateResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import get_object_or_404

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
        context = super(DecisionDetail, self).get_context_data(*args, **kwargs)
        context['organization'] = self.object.organization
        context['tab'] = self.object.status
        return context

class DecisionList(ListView):
    model = Decision

    #@method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        slug = kwargs.get('org_slug', None)
        self.organization = get_object_or_404(Organization, slug=slug)
        return super(DecisionList, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.status = kwargs.get('status', Decision.PROPOSAL_STATUS)
        self.order = request.GET.get('sort', '-id')
        self.set_paginate_by(request)
        return super(DecisionList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        if self.order == 'feedback':
            qs = Decision.objects.order_by_count(self.order)
        elif self.order in ['decided_date', 'effective_date', 'review_date', 'expiry_date', 'deadline', 'archived_date']:
            qs = Decision.objects.order_null_last(self.order)
        else:
            qs = Decision.objects.order_by(self.order)
        qs = qs.filter(status=self.status).filter(organization=self.organization)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(DecisionList, self).get_context_data(**kwargs)
        context['organization'] = self.organization
        context['tab'] = self.status
        context['sort'] = self.order
        context['num'] = self.paginate_by
        context['prevstring'] = self.build_prev_query_string(context)
        context['nextstring'] = self.build_next_query_string(context)
        return context

    def set_paginate_by(self, request):
        # NB Don't know how to handle invalid Page # - https://docs.djangoproject.com/en/1.4/ref/class-based-views/
        # "Note that page must be either a valid page number or the value last; any other value for page will result in a 404 error."

        # The default number of items to paginate by        
        self.default_num_items = '10'
        
        page_num = request.GET.get('page')
        num_num = request.GET.get('num')
        
        # Clean-up if invalid num request was given (i.e. handles error silently)
        if num_num:
            try:
                num_num_int = int(num_num)
                if num_num_int <= 0: raise ValueError
            except ValueError:
                request.session['num'] = self.paginate_by = self.default_num_items
                return

        # Set to default in case where a link has been sent that includes page number, but doesn't include a num
        if page_num and not num_num:
            self.paginate_by = self.default_num_items

        # Standard case        
        else:
            self.paginate_by = request.GET.get('num', request.session.get('num', self.default_num_items))
        
        # Finally set as user's session value
        request.session['num'] = self.paginate_by
    
    def build_prev_query_string(self, context):
        if not context['page_obj']:
            return None
        else:
            return self.build_query_string(context, context['page_obj'].previous_page_number())

    def build_next_query_string(self, context):
        if not context['page_obj']:
            return None
        else:
            return self.build_query_string(context, context['page_obj'].next_page_number())

    def build_query_string(self, context, page_num):
        page_query = 'page=' + str(page_num)
        #prepend non-default number of items per page
        if not context['num'] == self.default_num_items:
            page_query = 'num=' + str(context['num']) + '&' + page_query
        #prepend non-default sort
        if not context['sort'] == '-id':
            page_query = 'sort=' + context['sort'] + '&' + page_query
        return '?' + page_query


class DecisionCreate(CreateView):
    model = Decision
    form_class = DecisionForm
    status = Decision.PROPOSAL_STATUS
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.status = kwargs.get('status', Decision.PROPOSAL_STATUS)
        slug = kwargs.get('org_slug', None)
        self.organization = Organization.active.get(slug=slug)
        return super(DecisionCreate, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return super(DecisionCreate, self).get(*args, **kwargs)
        
    def get_form(self, form):
        form = super(DecisionCreate, self).get_form(form)
        form.fields['status'].initial = self.status
        return form
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.editor = self.request.user
        form.instance.last_status = 'new'
        form.instance.organization = self.organization
        return super(DecisionCreate, self).form_valid(form)
    
    def get_context_data(self, *args, **kwargs):
        context = super(DecisionCreate, self).get_context_data(**kwargs)
        context['organization'] = self.organization
        context['tab'] = self.status
        return context

    def get_success_url(self, *args, **kwargs):
        return reverse('publicweb_item_list', args=[self.organization.slug, self.status])

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
        object = self.get_object()
        status = object.status
        slug = object.organization.slug
        return reverse('publicweb_item_list', args=[slug, status])

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

