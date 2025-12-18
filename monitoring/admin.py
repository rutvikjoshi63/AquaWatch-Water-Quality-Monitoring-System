from django.contrib import admin
from .models import WaterBody, WaterQualityMeasurement

# Register your models here.
@admin.register(WaterBody)
class WaterBodyAdmin(admin.ModelAdmin):
    list_display = ['name', 'water_body_type', 'latitude', 'longitude']
    list_filter = ['water_body_type']
    search_fields = ['name']


@admin.register(WaterQualityMeasurement)
class WaterQualityMeasurementAdmin(admin.ModelAdmin):
    list_display = ['water_body', 'measured_at', 'ph']
    list_filter = ['water_body']
    search_fields = ['water_body__name']