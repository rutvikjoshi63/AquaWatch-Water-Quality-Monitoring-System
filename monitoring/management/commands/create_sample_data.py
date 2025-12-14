"""
Management command to create sample water quality data for testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import timedelta
import random
from monitoring.models import WaterBody, WaterQualityMeasurement


class Command(BaseCommand):
    help = 'Creates sample water bodies and measurements for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample water bodies...')
        
        # Sample water bodies across the US
        water_bodies_data = [
            {
                'name': 'Lake Michigan',
                'water_body_type': 'LAKE',
                'location': Point(-87.0073, 42.3601),
                'description': 'One of the five Great Lakes of North America',
                'regulatory_body': 'EPA Region 5'
            },
            {
                'name': 'Mississippi River',
                'water_body_type': 'RIVER',
                'location': Point(-90.1994, 38.6270),
                'description': 'Major river system in North America',
                'regulatory_body': 'EPA Region 7'
            },
            {
                'name': 'Lake Tahoe',
                'water_body_type': 'LAKE',
                'location': Point(-120.0324, 39.0968),
                'description': 'Large freshwater lake in the Sierra Nevada',
                'regulatory_body': 'EPA Region 9'
            },
            {
                'name': 'Chesapeake Bay',
                'water_body_type': 'OCEAN',
                'location': Point(-76.4813, 38.3235),
                'description': 'Largest estuary in the United States',
                'regulatory_body': 'EPA Region 3'
            },
            {
                'name': 'Colorado River',
                'water_body_type': 'RIVER',
                'location': Point(-111.7356, 35.0456),
                'description': 'Major river in the southwestern United States',
                'regulatory_body': 'EPA Region 9'
            }
        ]
        
        water_bodies = []
        for wb_data in water_bodies_data:
            wb, created = WaterBody.objects.get_or_create(
                name=wb_data['name'],
                defaults=wb_data
            )
            water_bodies.append(wb)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created: {wb.name}'))
            else:
                self.stdout.write(f'Already exists: {wb.name}')
        
        self.stdout.write('\nCreating sample measurements...')
        
        # Create measurements for the last 30 days
        researchers = ['Dr. Sarah Johnson', 'Dr. Mike Chen', 'Dr. Emily Rodriguez', 'Dr. James Wilson']
        
        measurements_created = 0
        for water_body in water_bodies:
            # Create 2-5 measurements per water body
            num_measurements = random.randint(2, 5)
            
            for i in range(num_measurements):
                # Random date within last 30 days
                days_ago = random.randint(0, 30)
                measured_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
                
                # Generate somewhat realistic values with occasional alerts
                ph = random.uniform(6.0, 8.8)
                dissolved_oxygen = random.uniform(4.0, 12.0)
                temperature = random.uniform(10.0, 28.0)
                turbidity = random.uniform(1.0, 8.0)
                nitrates = random.uniform(1.0, 12.0)
                phosphates = random.uniform(0.02, 0.15)
                ecoli_count = random.randint(10, 200)
                
                # Occasionally create measurements with alerts (20% chance)
                if random.random() < 0.2:
                    # Create an alert condition
                    alert_type = random.choice(['ph', 'do', 'temp', 'ecoli'])
                    if alert_type == 'ph':
                        ph = random.choice([random.uniform(5.0, 6.3), random.uniform(8.7, 9.5)])
                    elif alert_type == 'do':
                        dissolved_oxygen = random.uniform(2.0, 4.5)
                    elif alert_type == 'temp':
                        temperature = random.uniform(31.0, 35.0)
                    elif alert_type == 'ecoli':
                        ecoli_count = random.randint(150, 500)
                
                measurement = WaterQualityMeasurement.objects.create(
                    water_body=water_body,
                    measured_at=measured_at,
                    ph=round(ph, 2),
                    dissolved_oxygen=round(dissolved_oxygen, 2),
                    temperature=round(temperature, 1),
                    turbidity=round(turbidity, 2),
                    nitrates=round(nitrates, 2),
                    phosphates=round(phosphates, 3),
                    ecoli_count=ecoli_count,
                    measured_by=random.choice(researchers),
                    notes=f'Sample measurement #{i+1}',
                    location=water_body.location
                )
                measurements_created += 1
                
                # Show alert status
                if measurement.has_alerts:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  ⚠️  {water_body.name} - {measured_at.strftime("%Y-%m-%d")} - '
                            f'{len(measurement.get_alerts())} alert(s)'
                        )
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully created {measurements_created} measurements for {len(water_bodies)} water bodies'
            )
        )
        
        # Display summary
        total_alerts = sum(1 for m in WaterQualityMeasurement.objects.all() if m.has_alerts)
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Total measurements with alerts: {total_alerts}'
            )
        )
