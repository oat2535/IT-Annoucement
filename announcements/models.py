from django.db import models
import datetime
import re
import django.utils.text
from django.core.exceptions import SuspiciousFileOperation

# Fix Django stripping Thai vowels in uploaded filenames
def get_valid_filename_thai(name):
    s = str(name).strip().replace(" ", "_")
    # Allow Thai characters (\u0E00-\u0E7F) along with alphanumeric, dash, and dot.
    s = re.sub(r'(?u)[^-\w.\u0E00-\u0E7F]', '', s)
    if s in {"", ".", ".."}:
        raise SuspiciousFileOperation("Could not derive file name from '%s'" % name)
    return s

django.utils.text.get_valid_filename = get_valid_filename_thai

class Announcement(models.Model):
    change_no = models.CharField(max_length=50, unique=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=255)
    operate_date = models.CharField(max_length=100)
    operate_time = models.CharField(max_length=50)
    user_operate = models.CharField(max_length=200)
    remark = models.TextField(blank=True, null=True)

    @classmethod
    def get_next_change_no(cls):
        now = datetime.datetime.now()
        prefix = f"{now.strftime('%Y%m')}-IM"
        
        last_announcement = cls.objects.filter(change_no__contains='-IM').order_by('-id').first()
        
        if last_announcement:
            try:
                last_no = int(last_announcement.change_no.split('-IM')[-1])
                next_no = last_no + 1
            except ValueError:
                next_no = 16
        else:
            next_no = 16
            
        return f"{prefix}{next_no}"

    def save(self, *args, **kwargs):
        if not self.change_no:
            self.change_no = self.get_next_change_no()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.change_no} - {self.subject}"

# --- Dropdown Choice Models ---
class ChangeType(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self): return self.name

class ChangeCategory(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self): return self.name

class SystemAffected(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self): return self.name

class BranchLocation(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self): return self.name

class RiskLevel(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self): return self.name
# ------------------------------

class ChangeRequest(models.Model):
    request_no = models.CharField(max_length=50, unique=True, blank=True)
    # 0. การจัดประเภท (Categorization)
    change_type = models.ForeignKey(ChangeType, on_delete=models.SET_NULL, null=True, blank=True)
    change_category = models.ForeignKey(ChangeCategory, on_delete=models.SET_NULL, null=True, blank=True)
    system_affected = models.ForeignKey(SystemAffected, on_delete=models.SET_NULL, null=True, blank=True)
    branch_location = models.ForeignKey(BranchLocation, on_delete=models.SET_NULL, null=True, blank=True)
    risk_level = models.ForeignKey(RiskLevel, on_delete=models.SET_NULL, null=True, blank=True)

    # 1. ข้อมูลทั่วไปของโครงการ
    project_name = models.CharField(max_length=255)
    project_owner = models.CharField(max_length=255)
    objectives = models.TextField()
    contractor_company = models.CharField(max_length=255, blank=True, null=True)
    main_responsible_person = models.CharField(max_length=255)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    # 2. วัตถุประสงค์ของการใช้งาน
    usage_purpose = models.CharField(max_length=50, choices=[('new', 'ติดตั้งใหม่ (New Installation)'), ('modify', 'เปลี่ยนแปลงแก้ไข (Modify change)')], blank=True, null=True)
    usage_type = models.CharField(max_length=50, blank=True, null=True) # Dev, Test, UAT, Production (Comma separated or JSON, we can use CharField for simplicity if multiple are allowed)
    app_type = models.CharField(max_length=255, blank=True, null=True) # Web App, API, Database, Background Service
    infra_type = models.CharField(max_length=255, blank=True, null=True) # Hardware/System, Network, Firewall
    software_dev_test = models.CharField(max_length=50, blank=True, null=True) # มีการทดสอบ / ไม่มีการทดสอบ
    database_change = models.CharField(max_length=255, blank=True, null=True) # Master Data, Schema, Permission
    documents_provided = models.CharField(max_length=255, blank=True, null=True) # Installation plan, manual, etc.
    other_documents = models.TextField(blank=True, null=True)

    # 3. คุณลักษณะและความต้องการของ Resource
    vm_count = models.IntegerField(blank=True, null=True)
    require_public_ip = models.BooleanField(default=False)
    domain_name = models.CharField(max_length=255, blank=True, null=True)
    cpu_vcore = models.CharField(max_length=50, blank=True, null=True)
    ram_gb = models.CharField(max_length=50, blank=True, null=True)
    storage_gb = models.CharField(max_length=50, blank=True, null=True)
    os = models.CharField(max_length=50, blank=True, null=True) # Windows, Linux, Others
    os_version = models.CharField(max_length=100, blank=True, null=True)

    # 4. Network & Security
    ports = models.CharField(max_length=255, blank=True, null=True)
    has_authentication = models.BooleanField(default=False)
    access_type = models.CharField(max_length=100, blank=True, null=True) # ภายในองค์กร, จากภายนอก, ผ่าน VPN
    require_https = models.BooleanField(default=False)

    # 5. อื่นๆ
    expected_traffic = models.CharField(max_length=255, blank=True, null=True)
    dependencies = models.CharField(max_length=255, blank=True, null=True)
    require_dr_ha = models.BooleanField(default=False)
    additional_notes = models.TextField(blank=True, null=True)

    # 6. Signatures
    requester_name = models.CharField(max_length=255, blank=True, null=True)
    requester_date = models.DateField(blank=True, null=True)
    evaluator_name = models.CharField(max_length=255, blank=True, null=True)
    evaluator_date = models.DateField(blank=True, null=True)
    approver_name = models.CharField(max_length=255, blank=True, null=True)
    approver_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.request_no} - {self.project_name}"

    @classmethod
    def get_next_request_no(cls):
        now = datetime.datetime.now()
        prefix = f"CHG-{now.strftime('%Y')}-"
        
        last_request = cls.objects.filter(request_no__startswith=prefix).order_by('-id').first()
        
        if last_request and last_request.request_no:
            try:
                last_no = int(last_request.request_no.split(prefix)[-1])
                next_no = last_no + 1
            except ValueError:
                next_no = 1
        else:
            next_no = 1
            
        return f"{prefix}{next_no:04d}"

class ChangeRequestAttachment(models.Model):
    change_request = models.ForeignKey(ChangeRequest, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='change_requests/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment for {self.change_request.project_name}"
