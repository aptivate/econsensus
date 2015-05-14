from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.http import (HttpResponse, HttpResponseRedirect,
    HttpResponseForbidden, Http404)
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import View, RedirectView
from django.views.generic.detail import (DetailView,
    SingleObjectTemplateResponseMixin)
from django.views.generic.edit import ProcessFormView, ModelFormMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import get_object_or_404

import unicodecsv

from guardian.decorators import permission_required_or_403
from notification import models as notification
from organizations.models import Organization, OrganizationOwner, OrganizationUser
from haystack.views import SearchView
from waffle import switch_is_active

from publicweb.forms import (YourDetailsForm,
        NotificationSettingsForm, EconsensusActionItemCreateForm,
        EconsensusActionItemUpdateForm, ChangeOwnerForm, DecisionForm, FeedbackForm)
from publicweb.models import Decision, Feedback, NotificationSettings

from actionitems.models import ActionItem
from actionitems.views import (ActionItemCreateView, ActionItemUpdateView,
    ActionItemListView)
from django.core.urlresolvers import reverse
from signals.management import DECISION_CHANGE

class YourDetails(UpdateView):
    template_name = 'your_details.html'
    form_class = YourDetailsForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(YourDetails, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.add_message(
             self.request,
             messages.INFO,
             _('Your details have been updated successfully.')
        )
        return super(YourDetails, self).form_valid(form)

    def get_success_url(self):
        return reverse('your_details')


class ExportCSV(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.organization = Organization.active.get(
            slug=kwargs.get('org_slug', None)
        )
        if not self.organization.is_member(request.user):
            return HttpResponseForbidden(_("Whoops, wrong organization"))
        return super(ExportCSV, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        '''
        Create the HttpResponse object with the appropriate CSV header and
        corresponding CSV data from Decision, Feedback and Comment.
        Expected input: request (not quite sure what this is!)
        Expected output: http containing MIME info followed by the data itself
        as CSV.
        '''

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = ('attachment; '
               'filename=econsensus_decision_data_%s.csv' %
               unicode(self.organization.slug))

        def field_sorter(s):
            """
            Impose an order on certain fields.
            Fields not specified below will appear in arbitrary order at end of
            list.
            """
            if s == 'id': return '\t 00 %s' % s
            elif s == 'creation': return '\t 01 %s' % s
            elif s == 'submit_date': return '\t 02 %s' % s
            elif s == 'author': return '\t 03 %s' % s
            elif s == 'user': return '\t 04 %s' % s
            elif s == 'user_name': return '\t 05 %s' % s
            elif s == 'user_email': return '\t 06 %s' % s
            elif s == 'user_url': return '\t 07 %s' % s
            elif s == 'excerpt': return '\t 08 %s' % s
            elif s == 'description': return '\t 09 %s' % s
            elif s == 'budget': return '\t 10 %s' % s
            elif s == 'people': return '\t 11 %s' % s
            elif s == 'meeting_people': return '\t 12 %s' % s
            elif s == 'effective_date': return '\t 13 %s' % s
            elif s == 'deadline': return '\t 14 %s' % s
            elif s == 'expiry_date': return '\t 15 %s' % s
            elif s == 'review_date': return '\t 16 %s' % s
            elif s == 'tags': return '\t 17 %s' % s
            elif s == 'status': return '\t 18 %s' % s
            elif s == 'last_status': return '\t 19 %s' % s
            elif s == 'last_modified': return '\t 20 %s' % s
            elif s == 'editor': return '\t 21 %s' % s
            elif s == 'decided_date': return '\t 22 %s' % s
            elif s == 'archived_date': return '\t 23 %s' % s
            else: return s

        def remove_field(l, field_name):
            if field_name in l:
                l.remove(field_name)

        def field_value(obj, field_name):
            if isinstance(obj, Feedback) and field_name == 'rating':
                value = obj.get_rating_display()
            else:
                value = getattr(obj, field_name)
            return unicode(value).encode("utf-8", "replace")

        decision_field_names = sorted(
          list(
            set([field.name for field in Decision._meta.fields])
          ),
          key=field_sorter
        )
        feedback_field_names = sorted(
          list(
            set([field.name for field in Feedback._meta.fields])
          ),
          key=field_sorter)
        comment_field_names = sorted(list(set([field.name for field in Comment._meta.fields])), key=field_sorter)
        actionitem_field_names = sorted(list(set([field.name for field in ActionItem._meta.fields])), key=field_sorter)

        # Remove fields implied by filename (organization) or csv layout:
        remove_field(decision_field_names, 'organization')
        remove_field(feedback_field_names, 'decision')
        remove_field(comment_field_names, 'content_type')
        remove_field(comment_field_names, 'object_pk')
        remove_field(actionitem_field_names, 'origin')

        decision_column_titles = ["Issue.%s" % field_name for field_name in decision_field_names]
        feedback_column_titles = ["Feedback.%s" % field_name for field_name in feedback_field_names]
        comment_column_titles = ["Comment.%s" % field_name for field_name in comment_field_names]
        actionitem_column_titles = ["ActionItem.%s" % field_name for field_name in actionitem_field_names]

        writer = unicodecsv.writer(response)
        writer.writerow(decision_column_titles + feedback_column_titles +
                        comment_column_titles + actionitem_column_titles)

        no_decision_data = [u""] * len(decision_field_names)
        no_feedback_data = [u""] * len(feedback_field_names)
        no_comment_data = [u""] * len(comment_field_names)
        no_actionitem_data = [u""] * len(actionitem_field_names)

        for decision in Decision.objects.filter(organization=self.organization).order_by('id'):
            decision_data = [field_value(decision, field_name) for field_name in decision_field_names]
            writer.writerow(decision_data + no_feedback_data + no_comment_data + no_actionitem_data)

            for feedback in decision.feedback_set.all().order_by('id'):
                feedback_data = [field_value(feedback, field_name) for field_name in feedback_field_names]
                writer.writerow(no_decision_data + feedback_data + no_comment_data + no_actionitem_data)

                comments = Comment.objects.filter(
                    content_type=ContentType.objects.get_for_model(Feedback),
                    object_pk=feedback.id
                ).order_by('id')
                for comment in comments:
                    comment_data = [field_value(comment, field_name) for field_name in comment_field_names]
                    writer.writerow(no_decision_data + no_feedback_data + comment_data + no_actionitem_data)

            for actionitem in ActionItem.objects.filter(origin=decision.id).order_by('id'):
                actionitem_data = [field_value(actionitem, field_name) for field_name in actionitem_field_names]
                writer.writerow(no_decision_data + no_feedback_data + no_comment_data + actionitem_data)

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
        context['rating_names'] = [unicode(x) for x in Feedback.rating_names]
        if switch_is_active('actionitems'):
            context['actionitems'] = ActionItem.objects.filter(origin=self.kwargs['pk'])
        return context


class DecisionList(ListView):
    DEFAULT = Decision.DISCUSSION_STATUS

    model = Decision

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        slug = kwargs.get('org_slug', None)
        self.organization = get_object_or_404(Organization, slug=slug)
        return super(DecisionList, self).dispatch(request, *args, **kwargs)

    def set_status(self, **kwargs):
        self.status = kwargs.get('status', DecisionList.DEFAULT)
        return self.status

    def get(self, request, *args, **kwargs):
        self.set_status(**kwargs)
        self.set_sorting(request)
        self.get_table_headers(request)
        self.set_paginate_by(request)
        return super(DecisionList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        if self.sort_field in self.sort_by_count_fields:
            qs = Decision.objects.order_by_count(
                self.sort_field, self.sort_order)
        elif self.sort_field in self.sort_by_alpha_fields:
            qs = Decision.objects.order_by_case_insensitive(
                self.sort_field, self.sort_order)
        else:
            qs = Decision.objects.order_null_last(
                self.sort_order + self.sort_field)
        return qs.filter(
            status=self.status).filter(organization=self.organization)

    def get_context_data(self, *args, **kwargs):
        context = super(DecisionList, self).get_context_data(**kwargs)
        context['organization'] = self.organization
        context['tab'] = self.status
        context['sort'] = self.sort_order + self.sort_field
        context['header_list'] = self.header_list
        context['num'] = self.paginate_by
        context['prevstring'] = self.build_prev_query_string(context)
        context['nextstring'] = self.build_next_query_string(context)
        return context

    # SORTING ##########################################################

    # sort_options
    # * {'sort_field': 'default sort_order'}
    # * if the column is not in this dict, the sort will default to -id
    sort_options = {'id': '-',
                    'excerpt': '',
                    'feedback': '',
                    'deadline': '',
                    'last_modified': '-',
                    'decided_date': '-',
                    'review_date': '-',
                    'creation': '-',
                    'archived_date': '-'
                    }
    sort_by_count_fields = ['feedback']
    sort_by_alpha_fields = ['excerpt']

    sort_table_headers = {
       'discussion': ['id', 'watch', 'excerpt', 'feedback', 'deadline', 'last_modified'],
       'proposal': ['id', 'watch', 'excerpt', 'feedback', 'deadline', 'last_modified'],
       'decision': ['id', 'watch', 'excerpt', 'decided_date', 'review_date'],
       'archived': ['id', 'watch', 'excerpt', 'creation', 'archived_date']
    }

    unsortable_fields = ["watch"]

    def set_sorting(self, request):
        sort_request = request.GET.get('sort', '-id')
        if sort_request.startswith('-'):
            self.sort_order = '-'
            self.sort_field = sort_request.split('-')[1]
        else:
            self.sort_order = ''
            self.sort_field = sort_request
        # Invalid sort requests fail silently
        if not self.sort_field in self.sort_options:
            self.sort_order = '-'
            self.sort_field = 'id'

    def get_table_headers(self, request):
        # TODO How to handle this with internationalization
        header_titles = {'id': 'ID',
                         'watch': 'Watch',
                         'excerpt': 'Excerpt',
                         'feedback': 'Feedback',
                         'deadline': 'Deadline',
                         'last_modified': 'Last Modified',
                         'decided_date': 'Decided',
                         'review_date': 'Review',
                         'creation': 'Creation',
                         'archived_date': 'Archived'}

        self.header_list = []
        for header in self.sort_table_headers[self.status]:
                header = {
                    'attrs': header,
                    'path': self.get_sort_query(request, header),
                    'sortclass': self.get_sort_class(header),
                    'title': header_titles[header],
                    'unsortable': header in self.unsortable_fields
                }
                self.header_list.append(header)

    def get_sort_class(self, field):
        sort_class = ''
        if self.sort_field == field:
            sort_class = 'sort-asc'
            if self.sort_order == '-':
                sort_class = 'sort-desc'
        return sort_class

    def toggle_sort_order(self, sort_order):
        return '' if sort_order == '-' else '-'

    def get_sort_query(self, request, field):
        current_sort = self.sort_order + self.sort_field
        default_sort = self.sort_options.get(field, "") + field

        # Unless field is sort_field, when next_sort is inverse
        if current_sort == default_sort:
            next_sort_order = self.toggle_sort_order(self.sort_order)
            next_sort = "{0}{1}".format(next_sort_order, self.sort_field)
        else:
            next_sort = default_sort

        # Exception of next_sort='-id'
        if next_sort == '-id':
            sort_query = ''
        else:
            sort_query = '?sort=' + next_sort

        return request.path + sort_query

    # END SORTING ##########################################################

    # PAGINATION ##########################################################

    def set_paginate_by(self, request):
        # NB Don't know how to handle invalid Page # - https://docs.djangoproject.com/en/1.4/ref/class-based-views/
        # "Note that page must be either a valid page number or the value last;
        #       any other value for page will result in a 404 error."

        # The default number of items to paginate by
        self.default_num_items = '10'

        page_num = request.GET.get('page')
        num_num = request.GET.get('num')

        # Clean-up if invalid num request was given (i.e. handles error silently)
        if num_num:
            try:
                num_num_int = int(num_num)
                if num_num_int <= 0:
                    raise ValueError
            except ValueError:
                request.session['num'] = \
                    self.paginate_by = self.default_num_items
                return

        # Set to default in case where a link has been sent that includes page number, but doesn't include a num
        if page_num and not num_num:
            self.paginate_by = self.default_num_items

        # Standard case
        else:
            self.paginate_by = request.GET.get('num',
                request.session.get('num', self.default_num_items))

        # Finally set as user's session value
        request.session['num'] = self.paginate_by

    def build_prev_query_string(self, context):
        if not context['page_obj']:
            return None
        else:
            return self.build_query_string(context,
                context['page_obj'].previous_page_number())

    def build_next_query_string(self, context):
        if not context['page_obj']:
            return None
        else:
            return self.build_query_string(context,
                context['page_obj'].next_page_number())

    def build_query_string(self, context, page_num):
        page_query = 'page=' + str(page_num)
        # prepend non-default number of items per page
        if not context['num'] == self.default_num_items:
            page_query = 'num=' + str(context['num']) + '&' + page_query
        # prepend non-default sort
        if not context['sort'] == '-id':
            page_query = 'sort=' + context['sort'] + '&' + page_query
        return '?' + page_query

    # END PAGINATION ##########################################################


class DecisionCreate(CreateView):
    model = Decision
    form_class = DecisionForm
    status = Decision.PROPOSAL_STATUS

    @method_decorator(login_required)
    @method_decorator(
        permission_required_or_403(
            'edit_decisions_feedback',
            (Organization, 'slug', 'org_slug')
        )
    )
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
        status = getattr(self, 'object', self).status
        return reverse('publicweb_item_list',
                       args=[self.organization.slug, status])

    def post(self, *args, **kwargs):
        if self.request.POST.get('submit', None) == _("Cancel"):
            return HttpResponseRedirect(self.get_success_url())
        return super(DecisionCreate, self).post(*args, **kwargs)


class DecisionUpdate(UpdateView):
    model = Decision
    form_class = DecisionForm

    @method_decorator(login_required)
    @method_decorator(
        permission_required_or_403(
            'edit_decisions_feedback',
            (Organization, 'decision', 'pk')
        )
    )
    def dispatch(self, *args, **kwargs):
        return super(DecisionUpdate, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        form.instance.editor = self.request.user
        form.instance.last_status = self.last_status
        form.instance.minor_edit = form.cleaned_data['minor_edit']
        if (not form.cleaned_data['watch'] and
            notification.is_observing(self.object, self.request.user)):
            notification.stop_observing(self.object, self.request.user)
        elif (form.cleaned_data['watch'] and
              not notification.is_observing(self.object, self.request.user)):
            notification.observe(
                self.object,
                self.request.user,
                DECISION_CHANGE
            )

        return super(DecisionUpdate, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(DecisionUpdate, self).get_context_data(**kwargs)
        context['tab'] = self.object.status
        return context

    def get_success_url(self, *args, **kwargs):
        the_object = self.get_object()
        status = the_object.status
        slug = the_object.organization.slug
        return reverse('publicweb_item_list', args=[slug, status])

    def post(self, *args, **kwargs):
        if self.request.POST.get('submit', None) == _("Cancel"):
            return HttpResponseRedirect(self.get_success_url())
        else:
            self.last_status = self.get_object().status
            return super(DecisionUpdate, self).post(*args, **kwargs)


class FeedbackCreate(CreateView):
    model = Feedback
    form_class = FeedbackForm

    @method_decorator(login_required)
    @method_decorator(
        permission_required_or_403(
            'edit_decisions_feedback',
            (Organization, 'decision', 'parent_pk')
        )
    )
    def dispatch(self, request, *args, **kwargs):
        self.rating_initial = Feedback.COMMENT_STATUS
        rating = request.GET.get('rating')
        if rating:
            self.rating_initial = [value for value, name in Feedback.RATING_CHOICES if name == rating][0]
        return super(FeedbackCreate, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(FeedbackCreate, self).get_initial().copy()
        initial['rating'] = self.rating_initial
        return initial

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.decision = Decision.objects.get(pk=self.kwargs['parent_pk'])
        form.instance.last_status = 'new'
        return super(FeedbackCreate, self).form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse('publicweb_item_detail', args=[self.kwargs['parent_pk']])

    def post(self, *args, **kwargs):
        if self.request.POST.get('submit', None) == _("Cancel"):
            return HttpResponseRedirect(self.get_success_url())
        return super(FeedbackCreate, self).post(*args, **kwargs)


class FeedbackSnippetCreate(FeedbackCreate):
    def get_success_url(self, *args, **kwargs):
        return reverse('publicweb_feedback_snippet_detail',
                       args=[self.object.pk])


class FeedbackUpdate(UpdateView):
    model = Feedback
    form_class = FeedbackForm

    @method_decorator(login_required)
    @method_decorator(
        permission_required_or_403(
            'edit_decisions_feedback',
            (Organization, 'decision__feedback', 'pk')
        )
    )
    def dispatch(self, *args, **kwargs):
        return super(FeedbackUpdate, self).dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.request.POST.get('submit', None) == _("Cancel"):
            self.object = self.get_object()
            return HttpResponseRedirect(self.get_success_url())
        return super(FeedbackUpdate, self).post(*args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        form.instance.editor = self.request.user
        form.instance.minor_edit = form.cleaned_data['minor_edit']
        return super(FeedbackUpdate, self).form_valid(form, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(FeedbackUpdate, self).get_context_data(**kwargs)
        context['tab'] = self.object.decision.status
        return context

    def get_success_url(self, *args, **kwargs):
        return reverse('publicweb_item_detail', args=[self.object.decision.pk])


class EconsensusActionitemCreateView(ActionItemCreateView):
    template_name = 'actionitem_create_snippet.html'
    form_class = EconsensusActionItemCreateForm

    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('edit_decisions_feedback', (Organization, 'decision', 'pk')))
    def dispatch(self, *args, **kwargs):
        if not switch_is_active('actionitems'):
            raise Http404
        return super(EconsensusActionitemCreateView, self).dispatch(*args, **kwargs)

    def get_origin(self, request, *args, **kwargs):
        origin = self.kwargs.get('pk')
        return origin

    def get_success_url(self, *args, **kwargs):
        kwargs = {'decisionpk': self.kwargs.get('pk'),
                  'pk': self.object.pk}
        return reverse('actionitem_detail', kwargs=kwargs)


class EconsensusActionitemDetailView(DetailView):
    model = ActionItem
    template_name = 'actionitem_detail_snippet.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not switch_is_active('actionitems'):
            raise Http404
        return super(EconsensusActionitemDetailView, self).dispatch(*args, **kwargs)


class EconsensusActionitemUpdateView(ActionItemUpdateView):
    template_name = 'actionitem_update_snippet.html'
    form_class = EconsensusActionItemUpdateForm

    @method_decorator(login_required)
    @method_decorator(permission_required_or_403('edit_decisions_feedback', (Organization, 'decision', 'decisionpk')))
    def dispatch(self, *args, **kwargs):
        if not switch_is_active('actionitems'):
            raise Http404
        return super(EconsensusActionitemUpdateView, self).dispatch(*args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        kwargs = {'decisionpk': self.kwargs.get('decisionpk'),
                  'pk': self.object.pk}
        return reverse('actionitem_detail', kwargs=kwargs)

    def get_form_kwargs(self):
        kwargs = super(EconsensusActionitemUpdateView, self).get_form_kwargs()
        kwargs['prefix'] = "actionitem-{0}".format(self.object.id)
        return kwargs


class EconsensusActionitemListView(ActionItemListView):
    template_name = 'decision_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not switch_is_active('actionitems'):
            raise Http404
        self.organization = get_object_or_404(Organization, slug=kwargs.get('org_slug', None))
        return super(EconsensusActionitemListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.status = 'actionitems'
        self.set_sorting(request)
        self.get_table_headers(request)
        self.set_paginate_by(request)
        return super(EconsensusActionitemListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = ActionItem.objects \
                .filter(origin__organization=self.organization)
        if self.sort_field in self.sort_by_alpha_fields:
            qs = qs.extra(select={'lower': "lower(" + self.sort_field + ")"}).order_by(self.sort_order + 'lower')
        else:
            qs = qs.order_by(self.sort_order + self.sort_field)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(EconsensusActionitemListView, self).get_context_data(**kwargs)
        context['organization'] = self.organization
        context['tab'] = 'actionitems'
        context['sort'] = self.sort_order + self.sort_field
        context['header_list'] = self.header_list
        context['num'] = self.paginate_by
        context['prevstring'] = self.build_prev_query_string(context)
        context['nextstring'] = self.build_next_query_string(context)
        return context

    #######################################
    # TODO The following is NOT DRY
    #######################################

    # SORTING ##########################################################

    # sort_options
    # * {'sort_field': 'default sort_order'}
    # * if the column is not in this dict, the sort will default to -id
    sort_options = {'id': '-',
                    'description': '',
                    'responsible': '',
                    'deadline': '-',
                    'done': '-',
                    'origin': ''
                    }
    sort_by_alpha_fields = ['title', 'responsible']
    sort_table_headers = {'actionitems': ['id', 'description', 'responsible', 'deadline', 'done', 'origin']}

    def set_sorting(self, request):
        sort_request = request.GET.get('sort', '-id')
        if sort_request.startswith('-'):
            self.sort_order = '-'
            self.sort_field = sort_request.split('-')[1]
        else:
            self.sort_order = ''
            self.sort_field = sort_request
        # Invalid sort requests fail silently
        if not self.sort_field in self.sort_options:
            self.sort_order = '-'
            self.sort_field = 'id'

    def get_table_headers(self, request):
        # TODO How to handle this with internationalization
        header_titles = {'id': 'ID',
                         'description': 'Excerpt',
                         'responsible': 'Responsible',
                         'deadline': 'Deadline',
                         'done': 'Done?',
                         'origin': 'Parent Item',
                         }

        self.header_list = []
        for header in self.sort_table_headers[self.status]:
                header = {'attrs': header, 'path': self.get_sort_query(request, header), 'sortclass': self.get_sort_class(header), 'title': header_titles[header]}
                self.header_list.append(header)

    def get_sort_class(self, field):
        sort_class = ''
        if self.sort_field == field:
            sort_class = 'sort-asc'
            if self.sort_order == '-':
                sort_class = 'sort-desc'
        return sort_class

    def toggle_sort_order(self, sort_order):
        if sort_order == '-':
            toggled_sort_order = ''
        if sort_order == '':
            toggled_sort_order = '-'
        return toggled_sort_order

    def get_sort_query(self, request, field):
        current_sort = self.sort_order + self.sort_field
        default_sort = self.sort_options[field] + field

        # Unless field is sort_field, when next_sort is inverse
        if current_sort == default_sort:
            next_sort = self.toggle_sort_order(self.sort_order) + self.sort_field
        else:
            next_sort = default_sort

        # Exception of next_sort='-id'
        if next_sort == '-id':
            sort_query = ''
        else:
            sort_query = '?sort=' + next_sort

        return request.path + sort_query

    # END SORTING ##########################################################

    # PAGINATION ##########################################################

    def set_paginate_by(self, request):
        # NB Don't know how to handle invalid Page # -
        # https://docs.djangoproject.com/en/1.4/ref/class-based-views/
        # "Note that page must be either a valid page number or the value last;
        # any other value for page will result in a 404 error."

        # The default number of items to paginate by
        self.default_num_items = '10'

        page_num = request.GET.get('page')
        num_num = request.GET.get('num')

        # Clean-up if invalid num request was given
        # (i.e. handles error silently)
        if num_num:
            try:
                num_num_int = int(num_num)
                if num_num_int <= 0:
                    raise ValueError
            except ValueError:
                request.session['num'] = \
                    self.paginate_by = self.default_num_items
                return

        # Set to default in case where a link has been sent that includes page
        # number, but doesn't include a num
        if page_num and not num_num:
            self.paginate_by = self.default_num_items

        # Standard case
        else:
            num = request.session.get('num', self.default_num_items)
            self.paginate_by = request.GET.get('num', num)

        # Finally set as user's session value
        request.session['num'] = self.paginate_by

    def build_prev_query_string(self, context):
        if not context['page_obj']:
            return None
        else:
            return self.build_query_string(
                context,
                context['page_obj'].previous_page_number()
            )

    def build_next_query_string(self, context):
        if not context['page_obj']:
            return None
        else:
            return self.build_query_string(
                context,
                context['page_obj'].next_page_number()
            )

    def build_query_string(self, context, page_num):
        page_query = 'page=' + str(page_num)
        # prepend non-default number of items per page
        if not context['num'] == self.default_num_items:
            page_query = 'num=' + str(context['num']) + '&' + page_query
        # prepend non-default sort
        if not context['sort'] == '-id':
            page_query = 'sort=' + context['sort'] + '&' + page_query
        return '?' + page_query

    # END PAGINATION ##########################################################


class OrganizationRedirectView(RedirectView):
    '''
    If the user only belongs to one organization then
    take them to that organizations default Decision list page, otherwise
    take them to the organization list page.
    '''
    permanent = False

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(OrganizationRedirectView, self).dispatch(*args, **kwargs)

    def get_redirect_url(self):
        try:
            users_org = Organization.objects.get(users=self.request.user)
            return reverse('publicweb_item_list',
                args=[users_org.slug, DecisionList.DEFAULT]
            )
        except:
            return reverse('organization_list')


class UserNotificationSettings(ModelFormMixin, ProcessFormView,
        SingleObjectTemplateResponseMixin):
    model = NotificationSettings
    form_class = NotificationSettingsForm
    template_name = "notificationsettings_update.html"

    def get_success_url(self):
        return reverse('organization_list')

    def get_object(self):
        org_id = self.kwargs['org_slug']
        organization = Organization.objects.get(slug=org_id)

        try:
            the_object = self.model.objects.get(
               organization=organization.pk,
               user=self.request.user.pk
            )
        except self.model.DoesNotExist:
            the_object = self.model(
                organization=organization,
                user=self.request.user
            )

        return the_object

    def get_context_data(self, **kwargs):
        context = super(
            UserNotificationSettings,
            self
        ).get_context_data(**kwargs)
        context['organization'] = self.object.organization
        return context

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserNotificationSettings, self).dispatch(
               request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(UserNotificationSettings, self).get(
               request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.POST.get('submit', None) == _("Cancel"):
            return HttpResponseRedirect(self.get_success_url())
        return super(UserNotificationSettings, self).post(
              request,
              *args,
              **kwargs
        )


class DecisionSearchView(SearchView):
    DEFAULT_RESULTS_PER_PAGE = 10

    def __init__(self, *args, **kwargs):
        super(DecisionSearchView, self).__init__(*args, **kwargs)

    def __call__(self, request, org_slug):
        self.organization = get_object_or_404(Organization, slug=org_slug)

        num = request.GET.get('num')
        if not num: num = request.session.get('num')
        if not num: num = str(self.DEFAULT_RESULTS_PER_PAGE)
        request.session['num'] = num
        self.results_per_page = int(num)

        return super(DecisionSearchView, self).__call__(request)

    def get_results(self):
        results = super(DecisionSearchView, self).get_results()
        return results.filter(organization=self.organization)

    def extra_context(self):
        context = {}
        context['organization'] = self.organization
        context['tab'] = 'search'
        context['num'] = str(self.results_per_page)
        context['queryurl'] = self.build_query_link()
        context.update(super(DecisionSearchView, self).extra_context())
        return context

    def build_query_link(self):
        link = '?q=' + self.query
        if self.results_per_page != self.DEFAULT_RESULTS_PER_PAGE:
            link = link + '&num=' + str(self.results_per_page)
        return link

    # Might have been logical to call this method "as_view", but
    # that might imply that we inherit from View...
    @classmethod
    def make(cls):
        def search_view(request, *args, **kwargs):
            return cls()(request, *args, **kwargs)
        return login_required(search_view)


class BaseWatcherView(View):
    def get_object(self):
        object_id = self.kwargs['decision_id']
        decision = Decision.objects.get(pk=object_id)
        return decision

    def get_user(self):
        return self.request.user


class AddWatcher(BaseWatcherView):
    def get(self, request, *args, **kwargs):
        decision = self.get_object()
        user = self.get_user()
        notification.observe(decision, user, DECISION_CHANGE)
        return HttpResponseRedirect(request.GET['next'])


class RemoveWatcher(BaseWatcherView):
    def get(self, request, *args, **kwargs):
        decision = self.get_object()
        user = self.get_user()
        notification.stop_observing(decision, user)
        return HttpResponseRedirect(request.GET['next'])


class ChangeOwnerView(UpdateView):
    model = OrganizationOwner
    form_class = ChangeOwnerForm
    template_name_suffix = '_update_form'
    def get_success_url(self):
        return reverse('organization_admin',
                kwargs={'organization_pk': self.object.organization.pk})
    def get_form_kwargs(self):
        kwargs = super(ChangeOwnerView, self).get_form_kwargs()
        kwargs.update({'currentOrgPk': self.object.organization.pk})
        return kwargs