"""
Utility functions for AquaWatch monitoring system.
"""
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime


def export_data_to_excel(queryset):
    """
    Export water quality measurements to Excel file for regulatory compliance.
    
    Args:
        queryset: QuerySet of WaterQualityMeasurement objects
    
    Returns:
        HttpResponse with Excel file
    """
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Water Quality Data"
    
    # Define headers
    headers = [
        'Water Body', 'Water Body Type', 'Latitude', 'Longitude',
        'Measurement Date/Time', 'Measured By',
        'pH', 'Dissolved Oxygen (mg/L)', 'Temperature (°C)',
        'Turbidity (NTU)', 'Nitrates (mg/L)', 'Phosphates (mg/L)',
        'E. coli (CFU/100mL)', 'EPA Compliance Status', 'Alerts', 'Notes'
    ]
    
    # Style for header row
    header_fill = PatternFill(start_color='0066CC', end_color='0066CC', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')
    
    # Write headers
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Write data
    row_num = 2
    for measurement in queryset.select_related('water_body'):
        alerts = measurement.get_alerts()
        compliance_status = 'COMPLIANT' if not alerts else 'NON-COMPLIANT'
        alerts_text = '; '.join(alerts) if alerts else 'None'
        
        # Get location coordinates
        if measurement.sample_latitude and measurement.sample_longitude:
            lat = measurement.sample_latitude
            lon = measurement.sample_longitude
        else:
            lat = measurement.water_body.latitude
            lon = measurement.water_body.longitude
        
        row_data = [
            measurement.water_body.name,
            measurement.water_body.get_water_body_type_display(),
            lat,
            lon,
            measurement.measured_at.strftime('%Y-%m-%d %H:%M:%S'),
            measurement.measured_by,
            measurement.ph,
            measurement.dissolved_oxygen,
            measurement.temperature,
            measurement.turbidity,
            measurement.nitrates,
            measurement.phosphates,
            measurement.ecoli_count,
            compliance_status,
            alerts_text,
            measurement.notes
        ]
        
        for col, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_num, column=col, value=value)
            
            # Highlight non-compliant rows
            if compliance_status == 'NON-COMPLIANT' and col == 14:
                cell.fill = PatternFill(start_color='FFD700', end_color='FFD700', fill_type='solid')
                cell.font = Font(bold=True)
        
        row_num += 1
    
    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    # Add summary sheet
    summary_ws = wb.create_sheet("Summary")
    summary_ws['A1'] = 'AquaWatch Water Quality Export Summary'
    summary_ws['A1'].font = Font(bold=True, size=14)
    
    summary_ws['A3'] = 'Export Date:'
    summary_ws['B3'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    summary_ws['A4'] = 'Total Measurements:'
    summary_ws['B4'] = queryset.count()
    
    compliant_count = sum(1 for m in queryset if not m.has_alerts)
    summary_ws['A5'] = 'Compliant Measurements:'
    summary_ws['B5'] = compliant_count
    
    summary_ws['A6'] = 'Non-Compliant Measurements:'
    summary_ws['B6'] = queryset.count() - compliant_count
    
    # Create EPA Standards sheet
    standards_ws = wb.create_sheet("EPA Standards")
    standards_ws['A1'] = 'EPA Water Quality Standards Reference'
    standards_ws['A1'].font = Font(bold=True, size=14)
    
    from django.conf import settings
    standards = settings.EPA_STANDARDS
    
    standards_data = [
        ['Parameter', 'Standard', 'Unit'],
        ['pH (Minimum)', standards['ph_min'], 'pH units'],
        ['pH (Maximum)', standards['ph_max'], 'pH units'],
        ['Dissolved Oxygen (Minimum)', standards['dissolved_oxygen_min'], 'mg/L'],
        ['Temperature (Maximum)', standards['temperature_max'], '°C'],
        ['Turbidity (Maximum)', standards['turbidity_max'], 'NTU'],
        ['Nitrates (Maximum)', standards['nitrates_max'], 'mg/L'],
        ['Phosphates (Maximum)', standards['phosphates_max'], 'mg/L'],
        ['E. coli (Maximum)', standards['ecoli_max'], 'CFU/100mL'],
    ]
    
    for row_idx, row_data in enumerate(standards_data, start=3):
        for col_idx, value in enumerate(row_data, start=1):
            cell = standards_ws.cell(row=row_idx, column=col_idx, value=value)
            if row_idx == 3:  # Header row
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')
    
    # Prepare response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'aquawatch_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    
    wb.save(response)
    return response
