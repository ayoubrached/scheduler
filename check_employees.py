#!/usr/bin/env python
"""
Script to check and fix employee allowed_locations data
"""

from schedule.models import Employee, Location

def check_and_fix_employees():
    employees = Employee.objects.all()
    locations = Location.objects.all()
    
    print(f"Found {employees.count()} employees and {locations.count()} locations")
    
    for employee in employees:
        print(f"\nEmployee: {employee.first_name} {employee.last_name}")
        print(f"Allowed locations count: {employee.allowed_locations.count()}")
        
        if employee.allowed_locations.count() == 0:
            print("  -> No locations assigned, fixing...")
            # Assign all locations to this employee
            employee.allowed_locations.set(locations)
            print(f"  -> Now has {employee.allowed_locations.count()} locations")
        else:
            print("  -> Has locations assigned")
            for loc in employee.allowed_locations.all():
                print(f"    - {loc.name}")

if __name__ == "__main__":
    check_and_fix_employees() 