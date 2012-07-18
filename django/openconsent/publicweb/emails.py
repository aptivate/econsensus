from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.template import Context
from django.template import Template
from django.core.mail import EmailMessage
from livesettings import config_value

class OpenConsentEmailMessage(EmailMessage):
    
    def __init__(self, email_type, old_status, obj, *args, **kwargs):  # pylint: disable=R0914
        super(OpenConsentEmailMessage, self).__init__(*args, **kwargs)
        current_site = Site.objects.get_current()
        item_link = 'http://%s%s' % (current_site.domain, obj.get_absolute_url())
        subject_dict = {'id' : obj.id,
                        'status' : obj.status,
                        'excerpt': obj.excerpt.replace('\r\n', '') }
        body_dict = { 'site': current_site.name,
                     'author': obj.editor,
                     'description': obj.description,
                     'status': obj.status,
                     'old_status': old_status,
                     'link': item_link }
        if email_type == 'new':
            if obj.status == obj.DECISION_STATUS:
                subject_template = Template("[Econsensus]: Consensus Reached #{{ id }}: '{{ excerpt|safe }}'")
            else:
                subject_template = Template("[Econsensus]: New {{ status }} #{{ id }}: {{ excerpt|safe }}")

            body_template = get_template('email/new.txt')
            queryset = User.objects.all()
        elif email_type =='status':
            subject_template = Template("[Econsensus] -> {{ status }} #{{ id }}: {{ excerpt|safe }}")
            body_template = get_template('email/status_change.txt')
            queryset = User.objects.all()
        else:
            subject_template = Template("[Econsensus] {{ status }} #{{ id }}: Change to {{ excerpt|safe }}")
            body_template = get_template('email/content_change.txt')
            try:
                queryset = obj.watchers.exclude(username=obj.editor.username)
            except:
                queryset = obj.watchers.all()
        subject_context = Context(subject_dict)
        self.subject = subject_template.render(subject_context)

        body_context = Context(body_dict)            
        self.body = body_template.render(body_context)
        self.bcc = []        #pylint: disable-msg=C0103
        for this_user in queryset:
            if this_user.email:
                self.bcc.append(this_user.email)
        live_default = config_value('SendMail','DEFAULT_FROM_EMAIL')
        if live_default:
            self.from_email = live_default
        
    def __str__(self) :
        return str(self.__dict__)

    def __eq__(self, other) :
        self_dict = self.__dict__
        other_dict = other.__dict__
        del self_dict['connection']
        del other_dict['connection']

        return self_dict == other_dict
