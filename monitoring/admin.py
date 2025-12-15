"""
Admin interface for AquaWatch monitoring system.
"""
from django.contrib import admin
from .models import WaterBody, WaterQualityMeasurement


@admin.register(WaterBody)
class WaterBodyAdmin(admin.ModelAdmin):
    """
    Admin interface for WaterBody model.
    """
    list_display = ['name', 'water_body_type', 'regulatory_body', 
                   'monitoring_start_date', 'is_active']
    list_filter = ['water_body_type', 'is_active', 'monitoring_start_date']
    search_fields = ['name', 'description', 'regulatory_body']
    date_hierarchy = 'monitoring_start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'water_body_type', 'description')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Regulatory & Monitoring', {
            'fields': ('regulatory_body', 'monitoring_start_date', 'is_active')
        }),
    )


@admin.register(WaterQualityMeasurement)
class WaterQualityMeasurementAdmin(admin.ModelAdmin):
    """
    Admin interface for WaterQualityMeasurement model.
    """
    list_display = ['water_body', 'measured_at', 'ph', 'dissolved_oxygen',
                   'temperature', 'measured_by', 'has_alerts']
    list_filter = ['water_body', 'measured_at', 'measured_by']
    search_fields = ['water_body__name', 'measured_by', 'notes']
    date_hierarchy = 'measured_at'
    readonly_fields = ['created_at', 'quality_status', 'display_alerts']
    
    fieldsets = (
        ('Measurement Information', {
            'fields': ('water_body', 'measured_at', 'measured_by')
        }),
        ('Sample Location', {
            'fields': ('sample_latitude', 'sample_longitude')
        }),
        ('Water Quality Parameters', {
            'fields': ('ph', 'dissolved_oxygen', 'temperature', 'turbidity',
                      'nitrates', 'phosphates', 'ecoli_count')
        }),
        ('Quality Assessment', {
            'fields': ('quality_status', 'display_alerts')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def display_alerts(self, obj):
        """Display alerts as HTML list."""
        alerts = obj.get_alerts()
        if not alerts:
            return "No alerts - All parameters within EPA standards"
        return "<br>".join(f"⚠️ {alert}" for alert in alerts)
    
    display_alerts.short_description = 'EPA Standard Alerts'
    display_alerts.allow_tags = True
