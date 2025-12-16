"""
Tests for AquaWatch forms.
"""
import pytest
from django.utils import timezone
from monitoring.forms import WaterQualityMeasurementForm
from monitoring.models import WaterBody


@pytest.mark.django_db
class TestWaterQualityMeasurementForm:
    """Tests for WaterQualityMeasurementForm."""
    
    def test_valid_form(self, water_body):
        """Test form with valid data."""
        data = {
            'water_body': water_body.id,
            'measured_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'ph': 7.5,
            'dissolved_oxygen': 8.0,
            'temperature': 22.0,
            'turbidity': 3.0,
            'nitrates': 5.0,
            'phosphates': 0.08,
            'ecoli_count': 75,
            'measured_by': 'Test Researcher',
            'notes': 'Test notes',
            'latitude': 37.0902,
            'longitude': -95.7129
        }
        
        form = WaterQualityMeasurementForm(data=data)
        assert form.is_valid()
    
    def test_invalid_ph(self, water_body):
        """Test form with invalid pH."""
        data = {
            'water_body': water_body.id,
            'measured_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'ph': 15.0,  # Invalid
            'dissolved_oxygen': 8.0,
            'temperature': 22.0,
            'turbidity': 3.0,
            'nitrates': 5.0,
            'phosphates': 0.08,
            'ecoli_count': 75,
            'measured_by': 'Test'
        }
        
        form = WaterQualityMeasurementForm(data=data)
        assert not form.is_valid()
    
    def test_invalid_coordinates(self, water_body):
        """Test form with invalid coordinates."""
        data = {
            'water_body': water_body.id,
            'measured_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'ph': 7.5,
            'dissolved_oxygen': 8.0,
            'temperature': 22.0,
            'turbidity': 3.0,
            'nitrates': 5.0,
            'phosphates': 0.08,
            'ecoli_count': 75,
            'measured_by': 'Test',
            'latitude': 95.0,  # Invalid latitude
            'longitude': -95.7129
        }
        
        form = WaterQualityMeasurementForm(data=data)
        assert not form.is_valid()
    
    def test_form_saves_location(self, water_body):
        """Test form correctly saves location coordinates."""
        data = {
            'water_body': water_body.id,
            'measured_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'ph': 7.5,
            'dissolved_oxygen': 8.0,
            'temperature': 22.0,
            'turbidity': 3.0,
            'nitrates': 5.0,
            'phosphates': 0.08,
            'ecoli_count': 75,
            'measured_by': 'Test',
            'latitude': 40.7128,
            'longitude': -74.0060
        }
        
        form = WaterQualityMeasurementForm(data=data)
        assert form.is_valid()
        measurement = form.save()
        
        assert measurement.sample_latitude is not None
        assert measurement.sample_longitude is not None
        assert abs(measurement.sample_latitude - 40.7128) < 0.0001
        assert abs(measurement.sample_longitude - (-74.0060)) < 0.0001
