import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Announcement

def index(request):
    next_change_no = Announcement.get_next_change_no()
    all_announcements = Announcement.objects.all().order_by('-id')
    return render(request, 'announcements/IT_Annoucement.html', {
        'next_change_no': next_change_no,
        'all_announcements': all_announcements
    })

@csrf_exempt
def save_announcement(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            change_no = data.get('change_no', '').strip()
            if change_no:
                try:
                    announcement = Announcement.objects.get(change_no=change_no)
                    announcement.subject = data.get('subject', '')
                    announcement.operate_date = data.get('operate_date', '')
                    announcement.operate_time = data.get('operate_time', '')
                    announcement.user_operate = data.get('user_operate', '')
                    announcement.remark = data.get('remark', '')
                    announcement.save()
                except Announcement.DoesNotExist:
                    # Create a new announcement from the received data if not exists somehow
                    announcement = Announcement(
                        change_no=change_no,
                        subject=data.get('subject', ''),
                        operate_date=data.get('operate_date', ''),
                        operate_time=data.get('operate_time', ''),
                        user_operate=data.get('user_operate', ''),
                        remark=data.get('remark', '')
                    )
                    announcement.save()
            else:
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

def get_announcement(request):
    change_no = request.GET.get('change_no', '').strip()
    if change_no:
        try:
            announcement = Announcement.objects.get(change_no=change_no)
            return JsonResponse({
                'status': 'success',
                'data': {
                    'change_no': announcement.change_no,
                    'subject': announcement.subject,
                    'operate_date': announcement.operate_date,
                    'operate_time': announcement.operate_time,
                    'user_operate': announcement.user_operate,
                    'remark': announcement.remark
                }
            })
        except Announcement.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'ไม่พบข้อมูล'})
    return JsonResponse({'status': 'error', 'message': 'ไม่ได้ระบุ Change No.'})

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

def change_request_view(request):
    from .models import ChangeRequest, ChangeType, ChangeCategory, SystemAffected, BranchLocation, RiskLevel, ChangeRequestAttachment
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    from django.forms.models import model_to_dict

    next_request_no = ChangeRequest.get_next_request_no()
    all_requests = ChangeRequest.objects.all().order_by('-id')
    
    request_no = request.GET.get('request_no')
    req_obj = None
    req_data_json = "{}"
    req_files = []
    
    if request_no:
        try:
            req_obj = ChangeRequest.objects.get(request_no=request_no)
            req_dict = model_to_dict(req_obj)
            # format dates for html input type="date"
            if req_obj.start_date: req_dict['start_date'] = req_obj.start_date.strftime('%Y-%m-%d')
            if req_obj.end_date: req_dict['end_date'] = req_obj.end_date.strftime('%Y-%m-%d')
            if req_obj.requester_date: req_dict['requester_date'] = req_obj.requester_date.strftime('%Y-%m-%d')
            if req_obj.evaluator_date: req_dict['evaluator_date'] = req_obj.evaluator_date.strftime('%Y-%m-%d')
            if req_obj.approver_date: req_dict['approver_date'] = req_obj.approver_date.strftime('%Y-%m-%d')
            
            req_data_json = json.dumps(req_dict, cls=DjangoJSONEncoder)
            
            attachments = ChangeRequestAttachment.objects.filter(change_request=req_obj)
            for att in attachments:
                req_files.append({
                    'name': att.file.name.split('/')[-1],
                    'url': att.file.url
                })
        except ChangeRequest.DoesNotExist:
            pass
    
    context = {
        'next_request_no': next_request_no,
        'current_request_no': req_obj.request_no if req_obj else next_request_no,
        'all_requests': all_requests,
        'change_types': ChangeType.objects.all(),
        'change_categories': ChangeCategory.objects.all(),
        'systems': SystemAffected.objects.all(),
        'branches': BranchLocation.objects.all(),
        'risks': RiskLevel.objects.all(),
        'req_obj': req_obj,
        'req_data_json': req_data_json,
        'req_files_json': json.dumps(req_files)
    }
    return render(request, 'announcements/change_request.html', context)

@csrf_exempt
def save_change_request(request):
    if request.method == 'POST':
        try:
            from .models import ChangeRequest, ChangeRequestAttachment
            # Parse form data
            data = request.POST
            
            def get_bool(key):
                return data.get(key) == 'true' or data.get(key) == 'on' or data.get(key) == '1'

            change_request = ChangeRequest(
                request_no=ChangeRequest.get_next_request_no(),
                change_type_id=data.get('change_type') if data.get('change_type') else None,
                change_category_id=data.get('change_category') if data.get('change_category') else None,
                system_affected_id=data.get('system_affected') if data.get('system_affected') else None,
                branch_location_id=data.get('branch_location') if data.get('branch_location') else None,
                risk_level_id=data.get('risk_level') if data.get('risk_level') else None,
                
                project_name=data.get('project_name', ''),
                project_owner=data.get('project_owner', ''),
                objectives=data.get('objectives', ''),
                contractor_company=data.get('contractor_company', ''),
                main_responsible_person=data.get('main_responsible_person', ''),
                start_date=data.get('start_date') if data.get('start_date') else None,
                end_date=data.get('end_date') if data.get('end_date') else None,
                
                usage_purpose=data.get('usage_purpose', ''),
                usage_type=data.get('usage_type', ''),
                app_type=data.get('app_type', ''),
                infra_type=data.get('infra_type', ''),
                software_dev_test=data.get('software_dev_test', ''),
                database_change=data.get('database_change', ''),
                documents_provided=data.get('documents_provided', ''),
                other_documents=data.get('other_documents', ''),
                
                vm_count=int(data.get('vm_count')) if data.get('vm_count') and data.get('vm_count').isdigit() else None,
                require_public_ip=get_bool('require_public_ip'),
                domain_name=data.get('domain_name', ''),
                cpu_vcore=data.get('cpu_vcore', ''),
                ram_gb=data.get('ram_gb', ''),
                storage_gb=data.get('storage_gb', ''),
                os=data.get('os', ''),
                os_version=data.get('os_version', ''),
                
                ports=data.get('ports', ''),
                has_authentication=get_bool('has_authentication'),
                access_type=data.get('access_type', ''),
                require_https=get_bool('require_https'),
                
                expected_traffic=data.get('expected_traffic', ''),
                dependencies=data.get('dependencies', ''),
                require_dr_ha=get_bool('require_dr_ha'),
                additional_notes=data.get('additional_notes', ''),
                
                requester_name=data.get('requester_name', ''),
                requester_date=data.get('requester_date') if data.get('requester_date') else None,
                evaluator_name=data.get('evaluator_name', ''),
                evaluator_date=data.get('evaluator_date') if data.get('evaluator_date') else None,
                approver_name=data.get('approver_name', ''),
                approver_date=data.get('approver_date') if data.get('approver_date') else None
            )
            change_request.save()

            files = request.FILES.getlist('attachments')
            for f in files:
                ChangeRequestAttachment.objects.create(change_request=change_request, file=f)

            return JsonResponse({
                'status': 'success', 
                'message': 'บันทึกข้อมูล Change Request เรียบร้อยแล้ว',
                'id': change_request.id,
                'request_no': change_request.request_no
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def get_change_request(request):
    request_no = request.GET.get('request_no')
    if not request_no:
        return JsonResponse({'status': 'error', 'message': 'Missing request_no parameter'}, status=400)
        
    try:
        from .models import ChangeRequest
        cr = ChangeRequest.objects.get(request_no=request_no)
        data = {
            'change_type': cr.change_type_id if cr.change_type_id else '',
            'change_category': cr.change_category_id if cr.change_category_id else '',
            'system_affected': cr.system_affected_id if cr.system_affected_id else '',
            'branch_location': cr.branch_location_id if cr.branch_location_id else '',
            'risk_level': cr.risk_level_id if cr.risk_level_id else '',
            
            'project_name': cr.project_name,
            'project_owner': cr.project_owner,
            'objectives': cr.objectives,
            'contractor_company': cr.contractor_company,
            'main_responsible_person': cr.main_responsible_person,
            'start_date': cr.start_date.isoformat() if cr.start_date else '',
            'end_date': cr.end_date.isoformat() if cr.end_date else '',
            'usage_purpose': cr.usage_purpose,
            'usage_type': cr.usage_type,
            'app_type': cr.app_type,
            'infra_type': cr.infra_type,
            'software_dev_test': cr.software_dev_test,
            'database_change': cr.database_change,
            'documents_provided': cr.documents_provided,
            'other_documents': cr.other_documents,
            'vm_count': cr.vm_count,
            'require_public_ip': cr.require_public_ip,
            'domain_name': cr.domain_name,
            'cpu_vcore': cr.cpu_vcore,
            'ram_gb': cr.ram_gb,
            'storage_gb': cr.storage_gb,
            'os': cr.os,
            'os_version': cr.os_version,
            'ports': cr.ports,
            'has_authentication': cr.has_authentication,
            'access_type': cr.access_type,
            'require_https': cr.require_https,
            'expected_traffic': cr.expected_traffic,
            'dependencies': cr.dependencies,
            'require_dr_ha': cr.require_dr_ha,
            'additional_notes': cr.additional_notes,
            'requester_name': cr.requester_name,
            'requester_date': cr.requester_date.isoformat() if cr.requester_date else '',
            'evaluator_name': cr.evaluator_name,
            'evaluator_date': cr.evaluator_date.isoformat() if cr.evaluator_date else '',
            'approver_name': cr.approver_name,
            'approver_date': cr.approver_date.isoformat() if cr.approver_date else '',
            'attachments': [{'id': att.id, 'name': att.file.name.split('/')[-1], 'url': att.file.url} for att in cr.attachments.all()]
        }
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=404)

def change_request_report_view(request):
    from .models import ChangeRequest
    from django.utils.dateparse import parse_date
    import datetime
    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    requests = []
    searched = False
    
    if start_date_str and end_date_str:
        searched = True
        try:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            
            if start_date and end_date:
                # Include the whole end_date
                end_date = end_date + datetime.timedelta(days=1)
                requests = ChangeRequest.objects.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date
                ).order_by('-id')
        except ValueError:
            pass
            
    context = {
        'requests': requests,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'searched': searched
    }
    return render(request, 'announcements/change_request_report.html', context)

def export_change_request_csv(request):
    from .models import ChangeRequest
    from django.utils.dateparse import parse_date
    import datetime
    import csv
    from django.http import HttpResponse
    
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    requests_query = ChangeRequest.objects.all().order_by('-id')
    
    if start_date_str and end_date_str:
        try:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if start_date and end_date:
                end_date = end_date + datetime.timedelta(days=1)
                requests_query = requests_query.filter(
                    created_at__gte=start_date,
                    created_at__lt=end_date
                )
        except ValueError:
            pass

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="change_request_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    # Header
    writer.writerow(['No.', 'Request No.', 'Project Name', 'Project Owner', 'Start Date', 'End Date', 'Create Date'])
    
    for i, req in enumerate(requests_query, 1):
        writer.writerow([
            i,
            req.request_no,
            req.project_name,
            req.project_owner,
            req.start_date.strftime("%Y-%m-%d") if req.start_date else "",
            req.end_date.strftime("%Y-%m-%d") if req.end_date else "",
            req.created_at.strftime("%Y-%m-%d %H:%M") if req.created_at else ""
        ])
        
    return response



def preview_document(request):
    import os
    from django.http import HttpResponse, Http404, JsonResponse
    from django.shortcuts import redirect
    
    attachment_id = request.GET.get('id')
    if not attachment_id:
        return JsonResponse({'status': 'error', 'message': 'Missing attachment id'}, status=400)
        
    try:
        from .models import ChangeRequestAttachment
        att = ChangeRequestAttachment.objects.get(id=attachment_id)
        
        original_path = att.file.path
        if not os.path.exists(original_path):
            return Http404("File not found")
            
        ext = os.path.splitext(original_path)[1].lower()
        
        if ext == '.pdf' or ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            return redirect(att.file.url)
            
        # We only strictly need this for Word now, but leaving Excel just in case
        if ext in ['.doc', '.docx', '.xls', '.xlsx']:
            pdf_path = os.path.splitext(original_path)[0] + '.pdf'
            
            if not os.path.exists(pdf_path):
                import subprocess
                
                # 1. Try LibreOffice first
                libreoffice_paths = [
                    'soffice',
                    'libreoffice',
                    r'C:\Program Files\LibreOffice\program\soffice.exe',
                    r'C:\Program Files (x86)\LibreOffice\program\soffice.exe'
                ]
                
                lo_success = False
                for lo_cmd in libreoffice_paths:
                    try:
                        subprocess.run([lo_cmd, '--version'], capture_output=True, check=True)
                        subprocess.run([
                            lo_cmd, '--headless', '--convert-to', 'pdf', 
                            os.path.abspath(original_path), '--outdir', os.path.dirname(os.path.abspath(original_path))
                        ], check=True)
                        if os.path.exists(pdf_path):
                            lo_success = True
                            break
                    except Exception:
                        continue
                
                # 2. Fallback to MS Office via win32com
                if not lo_success or not os.path.exists(pdf_path):
                    try:
                        import pythoncom
                        import win32com.client
                    except ImportError:
                        return JsonResponse({'status': 'error', 'message': 'LibreOffice is required for previewing Word documents on Linux servers.'}, status=500)
                    
                    pythoncom.CoInitialize()
                    try:
                        if ext in ['.doc', '.docx']:
                            word = win32com.client.Dispatch('Word.Application')
                            word.Visible = False
                            doc = word.Documents.Open(os.path.abspath(original_path))
                            doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)
                            doc.Close(False)
                            word.Quit()
                        elif ext in ['.xls', '.xlsx']:
                            excel = win32com.client.Dispatch('Excel.Application')
                            excel.Visible = False
                            excel.DisplayAlerts = False
                            wb = excel.Workbooks.Open(os.path.abspath(original_path))
                            wb.ExportAsFixedFormat(0, os.path.abspath(pdf_path))
                            wb.Close(False)
                            excel.Quit()
                    except Exception as e:
                        pythoncom.CoUninitialize()
                        return JsonResponse({'status': 'error', 'message': f'Error converting file: {str(e)}'}, status=500)
                    finally:
                        pythoncom.CoUninitialize()
            
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as pdf_file:
                    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'inline; filename="preview.pdf"'
                    return response
            else:
                return JsonResponse({'status': 'error', 'message': 'Failed to generate PDF'}, status=500)
                
        return redirect(att.file.url)
                
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


