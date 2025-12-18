from django import forms
from .models import WaterQualityMeasurement, WaterBody

class WaterQualityMeasurementForm(forms.ModelForm):
    class Meta:
        model = WaterQualityMeasurement
        fields = ['water_body', 'measured_at', 'ph', 'notes']
        widgets = {
            'measured_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'ph': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '14'}),
        }