"""
Views for AquaWatch water quality monitoring.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import WaterBody, WaterQualityMeasurement
from .forms import WaterQualityMeasurementForm
from .utils import export_data_to_excel


def dashboard(request):
    """
    Main dashboard with charts, maps, and alerts.
    """
    # Get recent measurements (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_measurements = WaterQualityMeasurement.objects.filter(
        measured_at__gte=thirty_days_ago
    ).select_related('water_body')
    
    # Statistics
    total_water_bodies = WaterBody.objects.filter(is_active=True).count()
    total_measurements = WaterQualityMeasurement.objects.count()
    recent_count = recent_measurements.count()
    
    # Get measurements with alerts
    measurements_with_alerts = [m for m in recent_measurements if m.has_alerts]
    
    # Get all water bodies with their latest measurement for map
    water_bodies_with_data = []
    for wb in WaterBody.objects.filter(is_active=True):
        latest = wb.measurements.first()
        water_bodies_with_data.append({
            'water_body': wb,
            'latest_measurement': latest,
            'has_alerts': latest.has_alerts if latest else False,
            'quality_status': latest.quality_status if latest else 'unknown'
        })
    
    # Prepare chart data (last 7 days average by water body)
    seven_days_ago = timezone.now() - timedelta(days=7)
    chart_data = []
    for wb in WaterBody.objects.filter(is_active=True)[:5]:  # Top 5 water bodies
        measurements = WaterQualityMeasurement.objects.filter(
            water_body=wb,
            measured_at__gte=seven_days_ago
        ).order_by('measured_at')
        
        if measurements.exists():
            chart_data.append({
                'name': wb.name,
                'data': [
                    {
                        'date': m.measured_at.strftime('%Y-%m-%d'),
                        'ph': m.ph,
                        'dissolved_oxygen': m.dissolved_oxygen,
                        'temperature': m.temperature,
                    }
                    for m in measurements
                ]
            })
    
    context = {
        'total_water_bodies': total_water_bodies,
        'total_measurements': total_measurements,
        'recent_count': recent_count,
        'alert_count': len(measurements_with_alerts),
        'measurements_with_alerts': measurements_with_alerts[:10],
        'water_bodies_with_data': water_bodies_with_data,
        'chart_data': chart_data,
    }
    
    return render(request, 'monitoring/dashboard.html', context)


def submit_measurement(request):
    """
    Form for field researchers to submit new measurements.
    """
    if request.method == 'POST':
        form = WaterQualityMeasurementForm(request.POST)
        if form.is_valid():
            measurement = form.save()
            messages.success(request, 'Measurement submitted successfully!')
            
            # Show alerts if any
            alerts = measurement.get_alerts()
            if alerts:
                for alert in alerts:
                    messages.warning(request, f'Alert: {alert}')
            
            return redirect('dashboard')
    else:
        form = WaterQualityMeasurementForm()
    
    return render(request, 'monitoring/submit_measurement.html', {'form': form})


def water_body_detail(request, pk):
    """
    Detail view for a specific water body showing all measurements.
    """
    water_body = get_object_or_404(WaterBody, pk=pk)
    measurements = water_body.measurements.all()[:50]
    
    # Statistics for this water body
    if measurements:
        stats = water_body.measurements.aggregate(
            avg_ph=Avg('ph'),
            avg_do=Avg('dissolved_oxygen'),
            avg_temp=Avg('temperature'),
            avg_turbidity=Avg('turbidity'),
        )
    else:
        stats = {}
    
    # Chart data for trends
    recent_measurements = water_body.measurements.all()[:30]
    chart_data = [
        {
            'date': m.measured_at.strftime('%Y-%m-%d %H:%M'),
            'ph': m.ph,
            'dissolved_oxygen': m.dissolved_oxygen,
            'temperature': m.temperature,
            'turbidity': m.turbidity,
        }
        for m in reversed(list(recent_measurements))
    ]
    
    context = {
        'water_body': water_body,
        'measurements': measurements,
        'stats': stats,
        'chart_data': chart_data,
    }
    
    return render(request, 'monitoring/water_body_detail.html', context)


def export_data(request):
    """
    Export data to Excel for regulatory compliance.
    """
    if request.method == 'POST':
        water_body_id = request.POST.get('water_body')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Build queryset with filters
        queryset = WaterQualityMeasurement.objects.all()
        
        if water_body_id:
            queryset = queryset.filter(water_body_id=water_body_id)
        
        if start_date:
            queryset = queryset.filter(measured_at__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(measured_at__lte=end_date)
        
        # Generate Excel file
        response = export_data_to_excel(queryset)
        return response
    
    # Show export form
    water_bodies = WaterBody.objects.filter(is_active=True)
    context = {'water_bodies': water_bodies}
    
    return render(request, 'monitoring/export_data.html', context)
