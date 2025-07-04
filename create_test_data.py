#!/usr/bin/env python
"""
Django management script to create test data for the scheduler app.
Run this with: python manage.py shell < create_test_data.py
"""

from schedule.models import Location, Employee, Shift
from datetime import datetime, timedelta
from django.utils import timezone

def create_test_data():
    # Clear existing data
    Shift.objects.all().delete()
    Employee.objects.all().delete()
    Location.objects.all().delete()
    
    # Create locations
    locations = [
        Location.objects.create(name="Downtown Hotel", address="123 Main St"),
        Location.objects.create(name="Airport Terminal A", address="456 Airport Blvd"),
        Location.objects.create(name="Shopping Mall", address="789 Retail Ave"),
        Location.objects.create(name="Office Complex", address="321 Business Dr"),
    ]
    
    # Create employees
    employees = [
        Employee.objects.create(first_name="John", last_name="Smith", phone_number="555-0101"),
        Employee.objects.create(first_name="Sarah", last_name="Johnson", phone_number="555-0102"),
        Employee.objects.create(first_name="Mike", last_name="Davis", phone_number="555-0103"),
        Employee.objects.create(first_name="Lisa", last_name="Wilson", phone_number="555-0104"),
        Employee.objects.create(first_name="Tom", last_name="Brown", phone_number="555-0105"),
    ]
    
    # Allow all employees to work at all locations
    for employee in employees:
        employee.allowed_locations.set(locations)
    
    # Create some sample shifts for the current week
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    # Create shifts for each day of the week
    for day_offset in range(7):
        current_date = start_of_week + timedelta(days=day_offset)
        
        # Morning shift at Downtown Hotel
        Shift.objects.create(
            employee=employees[0],
            location=locations[0],
            start_time=timezone.make_aware(datetime.combine(current_date, datetime.min.time().replace(hour=8))),
            status='CONFIRMED'
        )
        
        # Afternoon shift at Airport
        Shift.objects.create(
            employee=employees[1],
            location=locations[1],
            start_time=timezone.make_aware(datetime.combine(current_date, datetime.min.time().replace(hour=14))),
            status='CONFIRMED'
        )
        
        # Evening shift at Mall
        if day_offset < 5:  # Only weekdays
            Shift.objects.create(
                employee=employees[2],
                location=locations[2],
                start_time=timezone.make_aware(datetime.combine(current_date, datetime.min.time().replace(hour=18))),
                status='CONFIRMED'
            )
    
    print(f"Created {len(locations)} locations")
    print(f"Created {len(employees)} employees")
    print(f"Created {Shift.objects.count()} shifts")
    print("Test data created successfully!")

if __name__ == "__main__":
    create_test_data() 