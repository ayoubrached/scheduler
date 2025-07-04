# schedule/models.py

from django.db import models
import datetime

class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)
    # unavailable_days is a string of comma-separated integers e.g. "0,1" for Monday, Tuesday
    unavailable_days = models.CharField(max_length=20, blank=True)
    locations = models.ManyToManyField(Location, related_name='employees', blank=True)

    def __str__(self):
        return self.name

class EmployeeAvailability(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    start_time = models.TimeField(default=datetime.time(8, 0))
    end_time = models.TimeField(default=datetime.time(18, 0))
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.name} on {self.date} {'is available' if self.is_available else 'is not available'}"

class Shift(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date', 'start_time')

    def __str__(self):
        return f"{self.employee.name} at {self.location.name} on {self.date} from {self.start_time}"