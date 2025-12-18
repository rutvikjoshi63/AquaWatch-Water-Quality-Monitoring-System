from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .models import WaterBody, WaterQualityMeasurement
from .utils import export_data_to_excel

# Create your views here.
def index(request):
    total_water_bodies = WaterBody.objects.count()
    total_measurements = WaterQualityMeasurement.objects.count()
    water_bodies_with_data = []
    
    for wb in WaterBody.objects.all():
        water_bodies_with_data.append({
            'water_body': wb,
            'measurement_count': wb.measurements.count()
        })
    
    context = {
        'total_water_bodies': total_water_bodies,
        'total_measurements': total_measurements,
        'water_bodies_with_data': water_bodies_with_data,
    }
    return render(request, 'index.html', context)

def export_data(request):
    queryset = WaterQualityMeasurement.objects.all()
    response = export_data_to_excel(queryset)
    return response

@csrf_exempt
def submit_data(request):
    try:
        water_body, created = WaterBody.objects.get_or_create(
            name=request.POST['water_body'],
            defaults={
                'water_body_type': request.POST['water_body_type'],
                'latitude': float(request.POST['latitude']),
                'longitude': float(request.POST['longitude']),
            }
        )
        
        measured_at_str = request.POST['measured_at']
        measured_at = datetime.strptime(measured_at_str, '%Y-%m-%d')
        
        WaterQualityMeasurement.objects.create(
            water_body=water_body,
            measured_at=measured_at,
            ph=float(request.POST['ph']),
            dissolved_oxygen=float(request.POST['dissolved_oxygen']),
            temperature=float(request.POST['temperature']),
            notes=request.POST['notes']
        )
        
        return redirect('index')
        
    except Exception as e:
        pass
    
    return render(request, 'submit_data.html')
    