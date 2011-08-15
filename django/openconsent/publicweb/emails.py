from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.template import Context
from django.core.mail import EmailMessage

#work in progress... remove email sending from model save
class OpenConsentEmailMessage(EmailMessage):
    
    def __init__(self, type, object, old_object=None, *args, **kwargs):
        super(OpenConsentEmailMessage, self).__init__(*args, **kwargs)
        current_site = Site.objects.get_current()
        item_name = object.short_name
        item_link = 'http://%s%s' % (current_site.domain, object.get_absolute_url())
    
        #record newness before saving
        if type == 'new':
            self.subject = "Open Consent: A new item has been created."
            email_template = get_template('email/new.txt')
            email_dict = { 'site': current_site.name, 'name': item_name, 'link': item_link }
            queryset = User.objects.all()
            
        elif type == 'status_change':
            self.subject = "Open Consent: An item's status has changed."
            email_template = get_template('email/status_change.txt')
            email_dict = { 'site': current_site.name, 
                          'name': item_name,
                          'link': item_link,
                          'old':  old_object.status_text(),
                          'new': object.status_text()}
            queryset = User.objects.all()
        elif type == 'content_change':
            self.subject = "Open Consent: An item has been modified"
            email_template = get_template('email/content_change.txt')
            email_dict = { 'site': current_site.name, 'name': item_name, 'link': item_link }
            queryset = object.subscribers.all()

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