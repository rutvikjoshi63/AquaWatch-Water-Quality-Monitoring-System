"""
Models for AquaWatch water quality monitoring system.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class WaterBody(models.Model):
    """
    Represents a monitored water body (lake, river, reservoir, etc.)
    """
    WATER_BODY_TYPES = [
        ('LAKE', 'Lake'),
        ('RIVER', 'River'),
        ('RESERVOIR', 'Reservoir'),
        ('POND', 'Pond'),
        ('STREAM', 'Stream'),
        ('OCEAN', 'Ocean/Bay'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    water_body_type = models.CharField(max_length=20, choices=WATER_BODY_TYPES)
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)], 
                                  help_text="Latitude coordinate")
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)],
                                   help_text="Longitude coordinate")
    description = models.TextField(blank=True)
    regulatory_body = models.CharField(max_length=200, blank=True, 
                                      help_text="EPA region or local authority")
    monitoring_start_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Water Bodies"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_water_body_type_display()})"


class WaterQualityMeasurement(models.Model):
    """
    Stores individual water quality readings from field measurements.
    """
    water_body = models.ForeignKey(WaterBody, on_delete=models.CASCADE, 
                                   related_name='measurements')
    measured_at = models.DateTimeField(default=timezone.now,
                                      help_text="When the measurement was taken")
    
    # Water quality parameters
    ph = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(14.0)],
        help_text="pH level (0-14)"
    )
    dissolved_oxygen = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Dissolved oxygen in mg/L"
    )
    temperature = models.FloatField(
        help_text="Water temperature in Celsius"
    )
    turbidity = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Turbidity in NTU (Nephelometric Turbidity Units)"
    )
    nitrates = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Nitrate concentration in mg/L"
    )
    phosphates = models.FloatField(
        validators=[MinValueValidator(0.0)],
        help_text="Phosphate concentration in mg/L"
    )
    ecoli_count = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="E. coli bacterial count in CFU/100mL"
    )
    
    # Metadata
    measured_by = models.CharField(max_length=200, 
                                  help_text="Name of field researcher")
    notes = models.TextField(blank=True)
    sample_latitude = models.FloatField(null=True, blank=True,
                                        validators=[MinValueValidator(-90), MaxValueValidator(90)],
                                        help_text="Latitude where sample was taken")
    sample_longitude = models.FloatField(null=True, blank=True,
                                         validators=[MinValueValidator(-180), MaxValueValidator(180)],
                                         help_text="Longitude where sample was taken")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-measured_at']
        indexes = [
            models.Index(fields=['-measured_at']),
            models.Index(fields=['water_body', '-measured_at']),
        ]
    
    def __str__(self):
        return f"{self.water_body.name} - {self.measured_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_alerts(self):
        """
        Check measurements against EPA standards and return list of alerts.
        """
        from django.conf import settings
        alerts = []
        standards = settings.EPA_STANDARDS
        
        if self.ph < standards['ph_min'] or self.ph > standards['ph_max']:
            alerts.append(f"pH out of range: {self.ph}")
        
        if self.dissolved_oxygen < standards['dissolved_oxygen_min']:
            alerts.append(f"Low dissolved oxygen: {self.dissolved_oxygen} mg/L")
        
        if self.temperature > standards['temperature_max']:
            alerts.append(f"High temperature: {self.temperature}°C")
        
        if self.turbidity > standards['turbidity_max']:
            alerts.append(f"High turbidity: {self.turbidity} NTU")
        
        if self.nitrates > standards['nitrates_max']:
            alerts.append(f"High nitrates: {self.nitrates} mg/L")
        
        if self.phosphates > standards['phosphates_max']:
            alerts.append(f"High phosphates: {self.phosphates} mg/L")
        
        if self.ecoli_count > standards['ecoli_max']:
            alerts.append(f"High E. coli count: {self.ecoli_count} CFU/100mL")
        
        return alerts
    
    @property
    def has_alerts(self):
        """Returns True if any measurements exceed EPA standards."""
        return len(self.get_alerts()) > 0
    
    @property
    def quality_status(self):
        """Return overall quality status: excellent, good, fair, poor."""
        alert_count = len(self.get_alerts())
        if alert_count == 0:
            return 'excellent'
        elif alert_count <= 2:
            return 'good'
        elif alert_count <= 4:
            return 'fair'
        else:
            return 'poor'
