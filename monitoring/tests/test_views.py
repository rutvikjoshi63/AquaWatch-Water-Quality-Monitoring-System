"""
Tests for AquaWatch views.
"""
import pytest
from django.urls import reverse
from django.utils import timezone
from monitoring.models import WaterBody, WaterQualityMeasurement


@pytest.mark.django_db
class TestDashboardView:
    """Tests for dashboard view."""
    
    def test_dashboard_loads(self, client):
        """Test dashboard page loads successfully."""
        url = reverse('dashboard')
        response = client.get(url)
        assert response.status_code == 200
        assert b'Water Quality Monitoring Dashboard' in response.content
    
    def test_dashboard_shows_statistics(self, client, water_body, measurement):
        """Test dashboard displays statistics."""
        url = reverse('dashboard')
        response = client.get(url)
        assert response.status_code == 200
        assert 'total_water_bodies' in response.context
        assert 'total_measurements' in response.context
        assert response.context['total_water_bodies'] >= 1
        assert response.context['total_measurements'] >= 1
    
    def test_dashboard_shows_alerts(self, client, water_body):
        """Test dashboard displays alerts for non-compliant measurements."""
        # Create measurement with alerts
        WaterQualityMeasurement.objects.create(
            water_body=water_body,
            measured_at=timezone.now(),
            ph=5.0,  # Below EPA standard
            dissolved_oxygen=3.0,  # Below EPA standard
            temperature=20.0,
            turbidity=3.0,
            nitrates=5.0,
            phosphates=0.05,
            ecoli_count=50,
            measured_by="Test"
        )
        
        url = reverse('dashboard')
        response = client.get(url)
        assert response.status_code == 200
        assert response.context['alert_count'] > 0


@pytest.mark.django_db
class TestSubmitMeasurementView:
    """Tests for submit measurement view."""
    
    def test_submit_form_loads(self, client):
        """Test submit form page loads."""
        url = reverse('submit_measurement')
        response = client.get(url)
        assert response.status_code == 200
        assert b'Submit Water Quality Measurement' in response.content
    
    def test_submit_measurement_success(self, client, water_body):
        """Test submitting a valid measurement."""
        url = reverse('submit_measurement')
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
            'notes': 'Test measurement',
            'latitude': 37.0902,
            'longitude': -95.7129
        }
        
        response = client.post(url, data)
        assert response.status_code == 302  # Redirect after success
        assert WaterQualityMeasurement.objects.count() == 1
    
    def test_submit_invalid_measurement(self, client, water_body):
        """Test submitting invalid measurement data."""
        url = reverse('submit_measurement')
        data = {
            'water_body': water_body.id,
            'measured_at': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'ph': 15.0,  # Invalid pH
            'dissolved_oxygen': 8.0,
            'temperature': 22.0,
            'turbidity': 3.0,
            'nitrates': 5.0,
            'phosphates': 0.08,
            'ecoli_count': 75,
            'measured_by': 'Test Researcher'
        }
        
        response = client.post(url, data)
        assert response.status_code == 200  # Form redisplayed with errors
        assert WaterQualityMeasurement.objects.count() == 0


@pytest.mark.django_db
class TestWaterBodyDetailView:
    """Tests for water body detail view."""
    
    def test_water_body_detail_loads(self, client, water_body):
        """Test water body detail page loads."""
        url = reverse('water_body_detail', args=[water_body.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert water_body.name.encode() in response.content
    
    def test_water_body_detail_shows_measurements(self, client, water_body, measurement):
        """Test detail page shows measurements."""
        url = reverse('water_body_detail', args=[water_body.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert 'measurements' in response.context
        assert len(response.context['measurements']) > 0


@pytest.mark.django_db
class TestExportDataView:
    """Tests for export data view."""
    
    def test_export_form_loads(self, client):
        """Test export form page loads."""
        url = reverse('export_data')
        response = client.get(url)
        assert response.status_code == 200
        assert b'Export Water Quality Data' in response.content
    
    def test_export_data_success(self, client, measurement):
        """Test exporting data to Excel."""
        url = reverse('export_data')
        data = {}  # Export all data
        response = client.post(url, data)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert 'attachment' in response['Content-Disposition']
