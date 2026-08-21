from django.contrib import admin
from .models import Announcement, ChangeRequest, ChangeRequestAttachment, ChangeType, ChangeCategory, SystemAffected, BranchLocation, RiskLevel

@admin.register(ChangeType)
class ChangeTypeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ChangeType._meta.fields]

@admin.register(ChangeCategory)
class ChangeCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ChangeCategory._meta.fields]

@admin.register(SystemAffected)
class SystemAffectedAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SystemAffected._meta.fields]

@admin.register(BranchLocation)
class BranchLocationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BranchLocation._meta.fields]

@admin.register(RiskLevel)
class RiskLevelAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RiskLevel._meta.fields]

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'change_no', 'subject', 'operate_date', 'operate_time', 'user_operate', 'remark', 'create_date')
    search_fields = ('change_no', 'subject', 'user_operate')
    readonly_fields = ('change_no', 'create_date')

class ChangeRequestAttachmentInline(admin.TabularInline):
    model = ChangeRequestAttachment
    extra = 1

@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ChangeRequest._meta.fields]
    search_fields = ('project_name', 'project_owner', 'contractor_company')
    readonly_fields = ('created_at',)
    inlines = [ChangeRequestAttachmentInline]
