from django.conf import settings
from notification.models import ObservedItem, send

def send_observation_notices_for(observed, signal="post_save", extra_context=None, headers=None, from_email=settings.DEFAULT_FROM_EMAIL):
    """
    Send a notice for each registered user about an observed object.
    Over-riding notification.models.send_observation_notices_for() here because we need 
        to customise from_email on a case-by-case basis.
    """
    if extra_context is None:
        extra_context = {}
    observed_items = ObservedItem.objects.all_for(observed, signal)
    for observed_item in observed_items:
        extra_context.update({"observed": observed})
        send([observed_item.user], observed_item.notice_type.label, extra_context, headers, from_email=from_email)
    return observed_items

