from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from report import views
from report.models import CommcareReport
from report.utils import download_commcare_zip_report


class SiteTest(TestCase):

    def setUp(self):
        self._add_report_url = reverse(views.add_commcare_report)
        self._create_user_and_login()
        self._commcare_report_url = 'https://www.commcarehq.org/a/mvp-sauri/' \
                                    'reports/export/custom/e0ea969f871d0fb29' \
                                    '209cac1416731a3/download/?format=csv'

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

    def _add_commcare_report(self):
        post_data = {
            'status': CommcareReport.STATUS_ACTIVE,
            'name': 'De-ID Report > Infant > Visit',
            'source_url': self._commcare_report_url}
        response = self.client.post(self._add_report_url, post_data)
        return response

    def test_add_cc_report_view(self):
        count = CommcareReport.objects.all().count()
        response = self.client.get(self._add_report_url)
        self.assertEqual(response.status_code, 200)
        response = self._add_commcare_report()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CommcareReport.objects.all().count(), count + 1)

    def test_duplicate_cc_report(self):
        count = CommcareReport.objects.all().count()
        response = self._add_commcare_report()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CommcareReport.objects.all().count(), count + 1)
        response = self._add_commcare_report()
        self.assertContains(
            response,
            u"There already exists a report with the same name and url!",
            status_code=200)

    def test_dataset_refresh(self):
        response = self._add_commcare_report()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CommcareReport.objects.count() > 0)
        report = CommcareReport.objects.reverse()[0]
        report.dataset_id = None
        report.save()
        url = reverse(views.refresh_dataset, kwargs={'report_pk': report.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        report = CommcareReport.objects.get(pk=report.pk)
        self.assertIsNotNone(report.dataset_id)
        self.assertIsNot(report.dataset_id, '')

    def test_download_commcare_report(self):
        file_name = download_commcare_zip_report(
            self._commcare_report_url,
            settings.COMMCARE_USERNAME,
            settings.COMMCARE_PASSWORD
        )
        self.assertIsNotNone(file_name)
        self.assertIn("output", file_name)
        self.assertTrue(file_name.endswith('#.csv'))
