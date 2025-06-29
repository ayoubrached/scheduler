# schedule/models.py

from django.db import models
from datetime import timedelta # <--- ADD THIS IMPORT

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, blank=True)
    allowed_locations = models.ManyToManyField(Location, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Shift(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CALLED_OFF', 'Called Off'),
        ('NO_SHOW', 'No Show'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    # end_time = models.DateTimeField() # <--- REMOVE OR COMMENT OUT THIS LINE
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')

    def __str__(self):
        # Let's make this more descriptive
        start_date = self.start_time.strftime('%b %d, %Y') # e.g., Jun 25, 2025
        start_time_formatted = self.start_time.strftime('%I:%M %p') # e.g., 08:00 AM
        return f"{self.employee} at {self.location} on {start_date} starting at {start_time_formatted}"