import datetime
import json
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Announcement, ChangeRequest, ChangeType, ChangeCategory, SystemAffected, BranchLocation, RiskLevel
from .utils import format_operate_date_defaults


class FormatOperateDateDefaultsTests(TestCase):
    def test_known_date_formats_thai_and_english_text(self):
        thai_text, english_text = format_operate_date_defaults(datetime.date(2026, 5, 18))
        self.assertEqual(thai_text, 'วันจันทร์ที่ 18 พฤษภาคม 2569')
        self.assertEqual(english_text, 'Monday, 18 May 2026')


class IndexViewOperateDateTests(TestCase):
    def test_operate_date_defaults_to_today(self):
        response = self.client.get('/')

        expected_th, expected_en = format_operate_date_defaults(timezone.localdate())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expected_th)
        self.assertContains(response, expected_en)
        # Ensure static logo is used, not 200kb inline base64
        self.assertContains(response, '/static/logo.png')
        self.assertNotContains(response, 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAE4g')


class ChangeRequestViewTests(TestCase):
    def setUp(self):
        self.change_type = ChangeType.objects.create(name='Standard Change')
        self.cr = ChangeRequest.objects.create(
            request_no='CHG-2026-9999',
            project_name='Test Project Alpha',
            project_owner='Test Owner',
            objectives='Testing purposes',
            main_responsible_person='Lead Dev',
            change_type=self.change_type
        )

    def test_change_request_blank_form_view(self):
        response = self.client.get(reverse('change_request'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('next_request_no', response.context)
        self.assertIsNone(response.context['req_obj'])
        # Should include options to select existing requests
        self.assertContains(response, 'CHG-2026-9999')

    def test_change_request_view_with_existing_request_no(self):
        response = self.client.get(reverse('change_request') + '?request_no=CHG-2026-9999')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['req_obj'])
        self.assertEqual(response.context['req_obj'].project_name, 'Test Project Alpha')
        self.assertContains(response, 'Test Project Alpha')

    def test_save_change_request_api(self):
        post_data = {
            'project_name': 'New Beta Service',
            'project_owner': 'Owner Beta',
            'objectives': 'Beta objectives',
            'main_responsible_person': 'Engineer Beta',
            'change_type': self.change_type.id,
            'require_public_ip': 'true'
        }
        response = self.client.post(reverse('save_change_request'), data=post_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['request_no'].startswith('CHG-'))
        created = ChangeRequest.objects.filter(request_no=data['request_no']).first()
        self.assertIsNotNone(created)
        self.assertEqual(created.project_name, 'New Beta Service')
        self.assertTrue(created.require_public_ip)

    def test_get_change_request_api(self):
        response = self.client.get(reverse('get_change_request') + '?request_no=CHG-2026-9999')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['project_name'], 'Test Project Alpha')
        self.assertEqual(data['data']['change_type'], self.change_type.id)

    def test_get_change_request_not_found(self):
        response = self.client.get(reverse('get_change_request') + '?request_no=NON-EXISTENT')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data['status'], 'error')


class SecurityAndHttpsSettingsTests(TestCase):
    def test_secure_proxy_ssl_header_configured(self):
        from django.conf import settings
        self.assertEqual(settings.SECURE_PROXY_SSL_HEADER, ('HTTP_X_FORWARDED_PROTO', 'https'))

    def test_request_via_https_proxy_is_secure(self):
        response = self.client.get('/', HTTP_X_FORWARDED_PROTO='https')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.is_secure())
