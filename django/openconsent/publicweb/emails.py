from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.template import Context
from django.template import Template
from django.core.mail import EmailMessage

class OpenConsentEmailMessage(EmailMessage):
    
    def __init__(self, typ, obj, old_obj=None, *args, **kwargs):  # pylint: disable=R0914
        super(OpenConsentEmailMessage, self).__init__(*args, **kwargs)
        current_site = Site.objects.get_current()
        item_link = 'http://%s%s' % (current_site.domain, obj.get_absolute_url())
        try:
            old_status = getattr(old_obj, 'status')
        except:
            old_status = None
        subject_dict = {'status' : obj.status,
                        'excerpt': obj.excerpt.replace('\r\n', '') }
        body_dict = { 'site': current_site.name, 
                     'author': obj.author, 
                     'description': obj.description,
                     'status': obj.status,
                     'old_status': old_status,
                     'link': item_link }

        #record newness before saving
        if typ == 'new':
            if obj.status == obj.DECISION_STATUS:
                subject_template = Template("[Econsensus]: Consensus Reached: {{ excerpt|safe }}")
            else:
                subject_template = Template("[Econsensus]: New {{ status }}: {{ excerpt|safe }}")

            body_template = get_template('email/new.txt')
            queryset = User.objects.all()
            
        elif typ == 'status_change':
            subject_template = Template("[Econsensus] -> {{ status }}: {{ excerpt|safe }}")
            body_template = get_template('email/status_change.txt')
            queryset = User.objects.all()
        elif typ == 'content_change':
            subject_template = Template("[Econsensus]: Change to {{ excerpt|safe }}")
            body_template = get_template('email/content_change.txt')
            try:
                queryset = obj.watchers.exclude(username=obj.author.username)
            except:
                queryset = obj.watchers.all()
        subject_context = Context(subject_dict)
        self.subject = subject_template.render(subject_context)

        body_context = Context(body_dict)            
        self.body = body_template.render(body_context)
        self.to = []        #pylint: disable-msg=C0103
        for this_user in queryset:
            if this_user.email:
                self.to.append(this_user.email)

    def __str__(self) :
        return str(self.__dict__)

    def __eq__(self, other) :
        self_dict = self.__dict__
        other_dict = other.__dict__
        del self_dict['connection']
        del other_dict['connection']

        return self_dict == other_dict
