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


class PortalAndAnnouncementViewTests(TestCase):
    def test_portal_home_displays_service_options(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IT Service & Operations Portal')
        self.assertContains(response, 'IT Announcement')
        self.assertContains(response, 'Request Form')
        self.assertContains(response, reverse('announcement'))
        self.assertContains(response, reverse('change_request'))
        self.assertContains(response, '/static/logo.png')

    def test_portal_home_redirects_change_no_query_param(self):
        response = self.client.get('/?change_no=CHG-2026-0001')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/announcement/?change_no=CHG-2026-0001')

    def test_announcement_view_operate_date_defaults_to_today(self):
        response = self.client.get('/announcement/')
        expected_th, expected_en = format_operate_date_defaults(timezone.localdate())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expected_th)
        self.assertContains(response, expected_en)
        # Ensure static logo is used, not 200kb inline base64
        self.assertContains(response, '/static/logo.png')
        self.assertNotContains(response, 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAE4g')
        # Ensure modern navbar toolbar layout is rendered
        self.assertContains(response, 'toolbar-container')
        self.assertContains(response, 'toolbarScrollLeft')
        self.assertContains(response, 'toolbarScrollRight')
        self.assertContains(response, 'select-change-no')
        self.assertContains(response, 'custom-nav-select')
        self.assertContains(response, 'หน้าหลัก Portal')
        self.assertContains(response, 'Request Form')

    def test_announcement_toggle_system_and_flipper_structure(self):
        response = self.client.get('/announcement/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'toggleSystemState()')
        self.assertContains(response, 'id="flipper"')
        self.assertContains(response, 'id="capture-area-close"')
        self.assertContains(response, 'id="capture-area-open"')
        self.assertContains(response, 'nav-btn-switch')
        self.assertContains(response, 'สลับหน้าเปิดระบบ')
        # Ensure vanilla JS is used without unprotected $( calls that throw ReferenceError
        self.assertNotContains(response, '$(document).ready')


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
        self.assertContains(response, 'โหลดข้อมูลเอกสารเรียบร้อยแล้ว')

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
        self.assertEqual(data['project_name'], 'New Beta Service')
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

    def test_export_change_request_csv_all_columns(self):
        self.cr.require_public_ip = True
        self.cr.vm_count = 2
        self.cr.save()

        response = self.client.get(reverse('export_change_request_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('text/csv'))
        content = response.content.decode('utf-8-sig')
        lines = content.strip().split('\r\n')
        self.assertGreaterEqual(len(lines), 2)
        
        # Verify all 46 columns in header
        headers = lines[0].split(',')
        self.assertEqual(len(headers), 46)
        self.assertIn('เลขที่เอกสาร (Request No.)', lines[0])
        self.assertIn('ประเภทการเปลี่ยนแปลง (Change Type)', lines[0])
        self.assertIn('ต้องการ Public IP (Require Public IP)', lines[0])

        # Verify converted Thai values in row
        data_row = lines[1]
        self.assertIn('CHG-2026-9999', data_row)
        self.assertIn('Standard Change', data_row)
        self.assertIn('ต้องการ Public IP', data_row)
        self.assertIn('2 เครื่อง', data_row)

    def test_export_csv_prevents_formula_injection_and_name_error(self):
        # Specifically test that a dash '-' does not become '- vCore' (#NAME? in Excel)
        cr_with_dash = ChangeRequest.objects.create(
            request_no='CHG-2026-DASH',
            project_name='Test Dash Specs',
            change_type=self.change_type,
            cpu_vcore='-',
            ram_gb='-',
            storage_gb='-',
            domain_name='=cmd|/C calc!A0'
        )
        response = self.client.get(reverse('export_change_request_csv'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8-sig')

        # Ensure '- vCore' does NOT exist (which causes #NAME? in Excel)
        self.assertNotIn('- vCore', content)
        self.assertNotIn('- GB', content)

        # Ensure formula injection is neutralized with single quote
        self.assertIn("'=cmd|/C calc!A0", content)


class SecurityAndHttpsSettingsTests(TestCase):
    def test_secure_proxy_ssl_header_configured(self):
        from django.conf import settings
        self.assertEqual(settings.SECURE_PROXY_SSL_HEADER, ('HTTP_X_FORWARDED_PROTO', 'https'))

    def test_request_via_https_proxy_is_secure(self):
        response = self.client.get('/', HTTP_X_FORWARDED_PROTO='https')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.is_secure())
