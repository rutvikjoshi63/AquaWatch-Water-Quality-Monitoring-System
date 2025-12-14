"""
Tests for AquaWatch models.
"""
import pytest
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils import timezone
from monitoring.models import WaterBody, WaterQualityMeasurement


@pytest.mark.django_db
class TestWaterBody:
    """Tests for WaterBody model."""
    
    def test_create_water_body(self):
        """Test creating a water body."""
        wb = WaterBody.objects.create(
            name="Blue Lake",
            water_body_type="LAKE",
            location=Point(-95.7129, 37.0902),
            description="A beautiful blue lake",
            regulatory_body="EPA Region 7"
        )
        
        assert wb.name == "Blue Lake"
        assert wb.water_body_type == "LAKE"
        assert wb.latitude == 37.0902
        assert wb.longitude == -95.7129
        assert wb.is_active is True
    
    def test_water_body_str(self, water_body):
        """Test string representation."""
        assert str(water_body) == "Test Lake (Lake)"
    
    def test_water_body_coordinates(self, water_body):
        """Test coordinate properties."""
        assert water_body.latitude == 37.0902
        assert water_body.longitude == -95.7129


@pytest.mark.django_db
class TestWaterQualityMeasurement:
    """Tests for WaterQualityMeasurement model."""
    
    def test_create_measurement(self, water_body):
        """Test creating a measurement."""
        measurement = WaterQualityMeasurement.objects.create(
            water_body=water_body,
            measured_at=timezone.now(),
            ph=7.2,
            dissolved_oxygen=8.5,
            temperature=22.0,
            turbidity=2.5,
            nitrates=4.0,
            phosphates=0.08,
            ecoli_count=75,
            measured_by="John Doe"
        )
        
        assert measurement.ph == 7.2
        assert measurement.dissolved_oxygen == 8.5
        assert measurement.measured_by == "John Doe"
    
    def test_measurement_str(self, measurement):
        """Test string representation."""
        assert "Test Lake" in str(measurement)
    
    def test_measurement_no_alerts(self, measurement):
        """Test measurement with no EPA alerts."""
        alerts = measurement.get_alerts()
        assert len(alerts) == 0
        assert measurement.has_alerts is False
        assert measurement.quality_status == 'excellent'
    
    def test_measurement_ph_alert(self, water_body):
        """Test pH out of range alert."""
        measurement = WaterQualityMeasurement.objects.create(
            water_body=water_body,
            measured_at=timezone.now(),
            ph=5.5,  # Below EPA minimum
            dissolved_oxygen=8.0,
            temperature=20.0,
            turbidity=3.0,
            nitrates=5.0,
            phosphates=0.05,
            ecoli_count=50,
            measured_by="Test Researcher"
        )
        
        alerts = measurement.get_alerts()
        assert len(alerts) > 0
        assert any('pH' in alert for alert in alerts)
        assert measurement.has_alerts is True
    
    def test_measurement_high_ecoli_alert(self, water_body):
        """Test high E. coli count alert."""
        measurement = WaterQualityMeasurement.objects.create(
            water_body=water_body,
            measured_at=timezone.now(),
            ph=7.5,
            dissolved_oxygen=8.0,
            temperature=20.0,
            turbidity=3.0,
            nitrates=5.0,
            phosphates=0.05,
            ecoli_count=200,  # Above EPA maximum
            measured_by="Test Researcher"
        )
        
        alerts = measurement.get_alerts()
        assert any('coli' in alert.lower() for alert in alerts)
    
    def test_measurement_quality_status(self, water_body):
        """Test quality status calculation."""
        # Excellent: no alerts
        m1 = WaterQualityMeasurement.objects.create(
            water_body=water_body,
            measured_at=timezone.now(),
            ph=7.5, dissolved_oxygen=8.0, temperature=20.0,
            turbidity=3.0, nitrates=5.0, phosphates=0.05,
            ecoli_count=50, measured_by="Test"
        )
        assert m1.quality_status == 'excellent'
        
        # Poor: multiple alerts
        m2 = WaterQualityMeasurement.objects.create(
            water_body=water_body,
            measured_at=timezone.now(),
            ph=5.0, dissolved_oxygen=3.0, temperature=35.0,
            turbidity=10.0, nitrates=15.0, phosphates=0.5,
            ecoli_count=500, measured_by="Test"
        )
        assert m2.quality_status == 'poor'
    
    def test_ph_validation(self, water_body):
        """Test pH value validation."""
        with pytest.raises(ValidationError):
            measurement = WaterQualityMeasurement(
                water_body=water_body,
                measured_at=timezone.now(),
                ph=15.0,  # Invalid pH
                dissolved_oxygen=8.0,
                temperature=20.0,
                turbidity=3.0,
                nitrates=5.0,
                phosphates=0.05,
                ecoli_count=50,
                measured_by="Test"
            )
            measurement.full_clean()
