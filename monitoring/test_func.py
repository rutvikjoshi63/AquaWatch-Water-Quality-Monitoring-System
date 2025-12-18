from django.test import TestCase
import pytest
from django.core.exceptions import ValidationError
from monitoring.forms import WaterQualityMeasurementForm
from monitoring.models import WaterBody, WaterQualityMeasurement
# Create your tests here.

@pytest.mark.django_db
class TestModels:
    def test_water_body(self):
        wb = WaterBody.objects.create(
            name=" Lake",
            water_body_type="LAKE",
            latitude=37.2,
            longitude=-95.7
        )
        assert wb.name == " Lake"
        assert wb.latitude == 37.2
        assert str(wb) == " Lake (Lake)"
        
    def test_measurement(self):
        water_body = WaterBody.objects.create(
            name="River",
            water_body_type="RIVER",
            latitude=40.0,
            longitude=-90.0
        )
        m = WaterQualityMeasurement.objects.create(
            water_body=water_body,
            measured_at="2025-01-01",
            ph=7.2,
            dissolved_oxygen=8.5,
            temperature=15.0
        )
        assert m.ph == 7.2
        
        with pytest.raises(ValidationError):
            WaterQualityMeasurement(
                water_body=water_body,
                measured_at="2025-01-01",
                ph=15.0
            ).full_clean()