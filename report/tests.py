from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from report import views
from report.models import CommcareReport


class SiteTest(TestCase):

    def setUp(self):
        self._create_user_and_login()

    def _create_user(self, username, password):
        user, created = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.save()
        return  user

    def _login(self, username, password):
        client = Client()
        assert client.login(username=username, password=password)
        return client

    def _create_user_and_login(self, username='bob', password='bob'):
        self.user = self._create_user(username, password)
        self.client = self._login(username, password)
        self.anon = Client()

    def test_index_view(self):
        response = self.client.get(reverse(views.index))
        self.assertEqual(response.status_code, 200)

    def test_add_cc_report_view(self):
        count = CommcareReport.objects.all().count()
        url = reverse(views.add_commcare_report)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        post_data = {
            'status': CommcareReport.STATUS_ACTIVE,
            'name': 'De-ID Report > Infant > Visit',
            'source_url': 'https://www.commcarehq.org/a/mvp-sauri/'
                           'reports/export/custom/e0ea969f871d0fb292'
                           '09cac1416731a3/download/?format=csv'}
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CommcareReport.objects.all().count(), count + 1)