from django.test import TestCase
from django.contrib.auth.models import User


class OpenConsentTestCase(TestCase):
    def login(self):
        username = 'admin'
        password = 'aptivate'
        email = 'admin@aptivate.org'
        user = User.objects.create_user(username, email, password=password)
        user.save()
        self.client.login(username=username, password=password)
