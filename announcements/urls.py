from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/save_announcement/', views.save_announcement, name='save_announcement'),
    path('api/check_change_no/', views.check_change_no, name='check_change_no'),
    path('api/get_announcement/', views.get_announcement, name='get_announcement'),
    path('report/', views.report_view, name='report'),
    path('export_csv/', views.export_csv, name='export_csv'),
]
