from django.core.management.base import BaseCommand
from schedule.models import Location, Employee, EmployeeAvailability
from datetime import time

class Command(BaseCommand):
    help = 'Sets up sample availability data for employees'

    def handle(self, *args, **options):
        # Get existing employees and locations
        employees = Employee.objects.all()
        locations = Location.objects.all()
        
        if not employees.exists():
            self.stdout.write(
                self.style.WARNING('No employees found. Please create employees first.')
            )
            return
            
        if not locations.exists():
            self.stdout.write(
                self.style.WARNING('No locations found. Please create locations first.')
            )
            return
        
        # Clear existing availability data
        EmployeeAvailability.objects.all().delete()
        
        # Create availability for each employee
        for employee in employees:
            # Set availability for weekdays (Monday-Friday)
            for day in range(5):  # 0=Monday, 1=Tuesday, etc.
                # Random availability patterns
                if day < 3:  # Monday-Wednesday: 8 AM - 6 PM
                    EmployeeAvailability.objects.create(
                        employee=employee,
                        day_of_week=day,
                        start_time=time(8, 0),
                        end_time=time(18, 0),
                        is_available=True
                    )
                elif day == 3:  # Thursday: 9 AM - 5 PM
                    EmployeeAvailability.objects.create(
                        employee=employee,
                        day_of_week=day,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        is_available=True
                    )
                else:  # Friday: 10 AM - 4 PM
                    EmployeeAvailability.objects.create(
                        employee=employee,
                        day_of_week=day,
                        start_time=time(10, 0),
                        end_time=time(16, 0),
                        is_available=True
                    )
            
            # Weekend availability (some employees available, some not)
            if employee.id % 2 == 0:  # Even ID employees work weekends
                for day in range(5, 7):  # Saturday and Sunday
                    EmployeeAvailability.objects.create(
                        employee=employee,
                        day_of_week=day,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        is_available=True
                    )
            else:  # Odd ID employees don't work weekends
                for day in range(5, 7):
                    EmployeeAvailability.objects.create(
                        employee=employee,
                        day_of_week=day,
                        start_time=time(0, 0),
                        end_time=time(0, 0),
                        is_available=False
                    )
        
        total_availability = EmployeeAvailability.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {total_availability} availability records for {employees.count()} employees'
            )
        ) 