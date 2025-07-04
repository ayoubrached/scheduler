from django.core.management.base import BaseCommand
from schedule.models import Shift

class Command(BaseCommand):
    help = 'Deletes all shifts from the database'

    def handle(self, *args, **options):
        Shift.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all shifts.')) 