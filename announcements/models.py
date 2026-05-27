from django.db import models
import datetime

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
