from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.template import Context
from django.template import Template
from django.core.mail import EmailMessage

#work in progress... remove email sending from model save
class OpenConsentEmailMessage(EmailMessage):
    
    def __init__(self, typ, obj, old_obj=None, *args, **kwargs):  # pylint: disable=R0914
        super(OpenConsentEmailMessage, self).__init__(*args, **kwargs)
        current_site = Site.objects.get_current()
        item_name = obj.description
        item_link = 'http://%s%s' % (current_site.domain, obj.get_absolute_url())
    
        #record newness before saving
        if typ == 'new':
            if obj.status == obj.DECISION_STATUS:
                subject_template = Template("[{{ site }} Econsensus]: Consensus Reached: {{ name|safe }}")
            else:
                subject_template = Template("[{{ site }} Econsensus]: New {{ status }}: {{ name|safe }}")

            subject_dict = {'site': current_site.name,
                            'status' : obj.status,
                            'name': obj.excerpt.replace('\r\n', '') }
            email_template = get_template('email/new.txt')
            email_dict = { 'site': current_site.name, 'name': item_name, 'link': item_link }
            queryset = User.objects.all()
            
        elif typ == 'status_change':
            subject_template = Template("[{{ site }} Econsensus]: {{ name|safe }} changed status from {{ old_status }} to {{ new_status }}")
            subject_dict = {'site': current_site.name,
                            'old_status' : old_obj.status,
                            'new_status' : obj.status,
                            'name': obj.excerpt.replace('\r\n', '') }
            email_template = get_template('email/status_change.txt')
            email_dict = { 'site': current_site.name, 
                          'name': item_name,
                          'link': item_link,
                          'old':  old_obj.status,
                          'new': obj.status}
            queryset = User.objects.all()
        elif typ == 'content_change':
            subject_template = Template("[{{ site }} Econsensus]: Change to {{ name|safe }}")
            subject_dict = {'site': current_site.name,
                            'name': obj.excerpt.replace('\r\n', '') }
            email_template = get_template('email/content_change.txt')
            email_dict = { 'site': current_site.name, 'name': item_name, 'link': item_link }
            try:
                queryset = obj.watchers.exclude(username=obj.author.username)
            except:
                queryset = obj.watchers.all()
        subject_context = Context(subject_dict)
        self.subject = subject_template.render(subject_context)

        email_context = Context(email_dict)            
        self.body = email_template.render(email_context)

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
