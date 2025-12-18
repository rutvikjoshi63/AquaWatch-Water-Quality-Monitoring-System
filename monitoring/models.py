from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class WaterBody(models.Model):
    WATER_BODY_TYPES = [
        ('LAKE', 'Lake'),
        ('RIVER', 'River'),
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
    def __str__(self):
        return f"{self.name} ({self.get_water_body_type_display()})"

class WaterQualityMeasurement(models.Model):
    water_body = models.ForeignKey(WaterBody, on_delete=models.CASCADE, 
                                   related_name='measurements')
    measured_at = models.DateTimeField(default=timezone.now,
                                      help_text="When the measurement was taken")
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
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.water_body.name} - {self.measured_at.strftime('%Y-%m-%d')}"
    