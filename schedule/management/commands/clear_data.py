from django.core.management.base import BaseCommand
from schedule.models import Location, Employee, Shift

class Command(BaseCommand):
    help = 'Clears all data from the scheduler app'

    def handle(self, *args, **options):
        # Clear all data
        shift_count = Shift.objects.count()
        employee_count = Employee.objects.count()
        location_count = Location.objects.count()
        
        Shift.objects.all().delete()
        Employee.objects.all().delete()
        Location.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {shift_count} shifts, {employee_count} employees, and {location_count} locations'
            )
        ) 