from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/save_announcement/', views.save_announcement, name='save_announcement'),
    path('report/', views.report_view, name='report'),
    path('export_csv/', views.export_csv, name='export_csv'),
]
