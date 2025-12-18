from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submit/', views.submit_data, name='submit_data'),
    path('export/', views.export_data, name='export_data'),
    
]
