from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.template import Context
from django.template import Template
from django.core.mail import EmailMessage

#work in progress... remove email sending from model save
class OpenConsentEmailMessage(EmailMessage):
    
    def __init__(self, type, object, old_object=None, *args, **kwargs):
        super(OpenConsentEmailMessage, self).__init__(*args, **kwargs)
        current_site = Site.objects.get_current()
        item_name = object.description
        item_link = 'http://%s%s' % (current_site.domain, object.get_absolute_url())
    
        #record newness before saving
        if type == 'new':
            if object.status == object.CONSENSUS_STATUS:
                subject_template = Template("[{{ site }} Open Consent]: Consensus Reached: {{ name|safe }}")
            else:
                subject_template = Template("[{{ site }} Open Consent]: New {{ status }}: {{ name|safe }}")

            subject_dict = {'site': current_site.name,
                            'status' : object.status_text(),
                            'name': object.excerpt.replace('\r\n', '') }
            email_template = get_template('email/new.txt')
            email_dict = { 'site': current_site.name, 'name': item_name, 'link': item_link }
            queryset = User.objects.all()
            
        elif type == 'status_change':
            subject_template = Template("[{{ site }} Open Consent]: {{ name|safe }} changed status from {{ old_status }} to {{ new_status }}")
            subject_dict = {'site': current_site.name,
                            'old_status' : old_object.status_text(),
                            'new_status' : object.status_text(),
                            'name': object.excerpt.replace('\r\n', '') }
            email_template = get_template('email/status_change.txt')
            email_dict = { 'site': current_site.name, 
                          'name': item_name,
                          'link': item_link,
                          'old':  old_object.status_text(),
                          'new': object.status_text()}
            queryset = User.objects.all()
        elif type == 'content_change':
            subject_template = Template("[{{ site }} Open Consent]: Change to {{ name|safe }}")
            subject_dict = {'site': current_site.name,
                            'name': object.excerpt.replace('\r\n', '') }
            email_template = get_template('email/content_change.txt')
            email_dict = { 'site': current_site.name, 'name': item_name, 'link': item_link }
            queryset = object.watchers.exclude(username=object.author.username)

        subject_context = Context(subject_dict)
        self.subject = subject_template.render(subject_context)

        email_context = Context(email_dict)            
        self.body = email_template.render(email_context)

        self.to = []        
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
