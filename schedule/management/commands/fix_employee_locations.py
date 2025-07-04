from django.core.management.base import BaseCommand
from schedule.models import Employee, Location

class Command(BaseCommand):
    help = 'Fixes employee allowed_locations by assigning all locations to employees who have none'

    def handle(self, *args, **options):
        employees = Employee.objects.all()
        locations = Location.objects.all()
        
        self.stdout.write(f"Found {employees.count()} employees and {locations.count()} locations")
        
        fixed_count = 0
        for employee in employees:
            self.stdout.write(f"\nEmployee: {employee.first_name} {employee.last_name}")
            self.stdout.write(f"Allowed locations count: {employee.allowed_locations.count()}")
            
            if employee.allowed_locations.count() == 0:
                self.stdout.write("  -> No locations assigned, fixing...")
                # Assign all locations to this employee
                employee.allowed_locations.set(locations)
                self.stdout.write(f"  -> Now has {employee.allowed_locations.count()} locations")
                fixed_count += 1
            else:
                self.stdout.write("  -> Has locations assigned")
                for loc in employee.allowed_locations.all():
                    self.stdout.write(f"    - {loc.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'\nFixed {fixed_count} employees with no allowed locations')
        ) 