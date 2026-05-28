import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Announcement

def index(request):
    next_change_no = Announcement.get_next_change_no()
    return render(request, 'announcements/IT_Annoucement.html', {'next_change_no': next_change_no})

@csrf_exempt
def save_announcement(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create a new announcement from the received data
            announcement = Announcement(
                subject=data.get('subject', ''),
                operate_date=data.get('operate_date', ''),
                operate_time=data.get('operate_time', ''),
                user_operate=data.get('user_operate', ''),
                remark=data.get('remark', '')
            )
            announcement.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': 'บันทึกข้อมูลเรียบร้อยแล้ว',
                'change_no': announcement.change_no
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def check_change_no(request):
    change_no = request.GET.get('change_no', '').strip()
    if change_no:
        exists = Announcement.objects.filter(change_no=change_no).exists()
    else:
        exists = False
    return JsonResponse({'exists': exists})

def report_view(request):
    from django.utils.dateparse import parse_date
    from datetime import datetime, timedelta
    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    announcements = []
    
    if start_date_str and end_date_str:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
        if start_date and end_date:
            end_date_inclusive = end_date + timedelta(days=1)
            announcements = Announcement.objects.filter(create_date__range=[start_date, end_date_inclusive]).order_by('-id')
            
    context = {
        'announcements': announcements,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'searched': bool(start_date_str and end_date_str)
    }
    return render(request, 'announcements/report.html', context)

def export_csv(request):
    import csv
    from django.http import HttpResponse
    from django.utils.dateparse import parse_date
    from datetime import datetime, timedelta
    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    announcements = []
    
    if start_date_str and end_date_str:
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
        if start_date and end_date:
            end_date_inclusive = end_date + timedelta(days=1)
            announcements = Announcement.objects.filter(create_date__range=[start_date, end_date_inclusive]).order_by('-id')
    else:
        announcements = Announcement.objects.all().order_by('-id')
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="it_announcement_report.csv"'
    
    # Write BOM for Excel compatibility with UTF-8
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow(['No.', 'Change No.', 'Subject', 'Operate Date', 'Operate Time', 'User Operate', 'Remark', 'Create Date'])
    
    for idx, item in enumerate(announcements, 1):
        create_date_formatted = item.create_date.strftime('%Y-%m-%d %H:%M') if item.create_date else ''
        writer.writerow([
            idx,
            item.change_no,
            item.subject,
            item.operate_date,
            item.operate_time,
            item.user_operate,
            item.remark,
            create_date_formatted
        ])
        
    return response
