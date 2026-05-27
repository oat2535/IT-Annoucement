from django.contrib import admin
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'change_no', 'subject', 'operate_date', 'operate_time', 'user_operate', 'remark', 'create_date')
    search_fields = ('change_no', 'subject', 'user_operate')
    readonly_fields = ('change_no', 'create_date')
