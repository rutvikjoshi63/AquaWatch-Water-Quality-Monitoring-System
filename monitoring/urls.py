"""
URL configuration for monitoring app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('submit/', views.submit_measurement, name='submit_measurement'),
    path('water-body/<int:pk>/', views.water_body_detail, name='water_body_detail'),
    path('export/', views.export_data, name='export_data'),
]
