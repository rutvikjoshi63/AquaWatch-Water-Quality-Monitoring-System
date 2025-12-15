"""
Forms for AquaWatch water quality monitoring.
"""
from django import forms
from .models import WaterQualityMeasurement, WaterBody


class WaterQualityMeasurementForm(forms.ModelForm):
    """
    Form for field researchers to submit water quality measurements.
    """
    latitude = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 40.7128',
            'step': 'any'
        }),
        help_text="Latitude of sample location"
    )
    longitude = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., -74.0060',
            'step': 'any'
        }),
        help_text="Longitude of sample location"
    )
    
    class Meta:
        model = WaterQualityMeasurement
        fields = [
            'water_body', 'measured_at', 'ph', 'dissolved_oxygen',
            'temperature', 'turbidity', 'nitrates', 'phosphates',
            'ecoli_count', 'measured_by', 'notes'
        ]
        widgets = {
            'water_body': forms.Select(attrs={'class': 'form-control'}),
            'measured_at': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'ph': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '14'
            }),
            'dissolved_oxygen': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0'
            }),
            'temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1'
            }),
            'turbidity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0'
            }),
            'nitrates': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0'
            }),
            'phosphates': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'ecoli_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'measured_by': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['latitude'].initial = self.instance.sample_latitude
            self.fields['longitude'].initial = self.instance.sample_longitude
    
    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        # Validate coordinate ranges
        if latitude is not None and (latitude < -90 or latitude > 90):
            raise forms.ValidationError('Latitude must be between -90 and 90')
        
        if longitude is not None and (longitude < -180 or longitude > 180):
            raise forms.ValidationError('Longitude must be between -180 and 180')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set sample location from latitude/longitude if provided
        latitude = self.cleaned_data.get('latitude')
        longitude = self.cleaned_data.get('longitude')
        if latitude is not None and longitude is not None:
            instance.sample_latitude = latitude
            instance.sample_longitude = longitude
        
        if commit:
            instance.save()
        return instance
