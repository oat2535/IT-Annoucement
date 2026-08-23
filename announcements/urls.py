from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/save_announcement/', views.save_announcement, name='save_announcement'),
    path('api/check_change_no/', views.check_change_no, name='check_change_no'),
    path('api/get_announcement/', views.get_announcement, name='get_announcement'),
    path('report/', views.report_view, name='report'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('change-request/', views.change_request_view, name='change_request'),
    path('api/save_change_request/', views.save_change_request, name='save_change_request'),
    path('api/get_change_request/', views.get_change_request, name='get_change_request'),
    path('api/preview_document/', views.preview_document, name='preview_document'),
    path('change-request-report/', views.change_request_report_view, name='change_request_report'),
    path('export_change_request_csv/', views.export_change_request_csv, name='export_change_request_csv'),
]
