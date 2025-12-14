import pytest
from django.contrib.gis.geos import Point
from django.utils import timezone
from monitoring.models import WaterBody, WaterQualityMeasurement


@pytest.fixture
def water_body():
    """Create a test water body."""
    return WaterBody.objects.create(
        name="Test Lake",
        water_body_type="LAKE",
        location=Point(-95.7129, 37.0902),
        description="A test water body",
        regulatory_body="EPA Region 7",
        monitoring_start_date=timezone.now().date()
    )


@pytest.fixture
def measurement(water_body):
    """Create a test measurement."""
    return WaterQualityMeasurement.objects.create(
        water_body=water_body,
        measured_at=timezone.now(),
        ph=7.5,
        dissolved_oxygen=8.0,
        temperature=20.0,
        turbidity=3.0,
        nitrates=5.0,
        phosphates=0.05,
        ecoli_count=50,
        measured_by="Test Researcher",
        location=Point(-95.7129, 37.0902)
    )
