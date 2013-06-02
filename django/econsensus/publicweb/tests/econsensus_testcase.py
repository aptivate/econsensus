from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.core.urlresolvers import reverse
from django.test import TestCase

from publicweb.models import Decision
from publicweb.tests.factories import UserFactory

class EconsensusTestCase(TestCase):

    def login_admin_user(self):
        admin_user = UserFactory(
            username = 'admin_editor',
            is_staff = True, 
            is_superuser = True)
        admin_user.set_password('test')
        admin_user.save()
        self.assertEqual(
            self.client.login(username=admin_user.username, password='test'), 
            True,
            "Failed to log in admin user"
        )
        return admin_user

    def change_decision_via_admin(self, decision, new_organization=None):
        """
        Used for testing custom behaviour for Decision change in django
        admin - see publicweb/admin.py, DecisionAdmin.save_model()
        Requirement: logged in user is_staff and is_superuser.
        """
        ma = ModelAdmin(Decision, AdminSite())
        data = ma.get_form(None)(instance=decision).initial
        for key, value in data.items():
            if value == None:
                data[key] = u''
        man_data = {
            'feedback_set-TOTAL_FORMS': u'1', 
            'feedback_set-INITIAL_FORMS': u'0', 
            'feedback_set-MAX_NUM_FORMS': u''
        }
        data.update(man_data)
        if new_organization:
            data['organization'] = new_organization.id

        url = reverse('admin:publicweb_decision_change', args=[decision.id])
        response = self.client.post(url, data, follow=True)
        self.assertEquals(
            response.template_name, 
            'admin/decision_change_list.html',
            "Failed to edit Decision via admin screen")

        decision = Decision.objects.get(id=decision.id)
        if new_organization:
            self.assertEquals(decision.organization.id, new_organization.id)
