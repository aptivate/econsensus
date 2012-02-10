from django.contrib.sites.models import Site

def current_site(request):
    '''
    A context processor to add the "current site" to the current Context
    http://bradmontgomery.blogspot.com/2009/01/add-context-processor-for-your-django.html
    '''
    try:
        current_site = Site.objects.get_current()
        return {
            'current_site': current_site,
        }
    except Site.DoesNotExist:
        # always return a dict, no matter what!
        return {'current_site':''} # an empty string