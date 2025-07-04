from rest_framework import serializers
from .models import Employee, EmployeeAvailability, Location, Shift
from datetime import datetime

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        # Tell the serializer which model it represents.
        model = Location
        # List the fields you want to include in the API output.
        fields = ['id', 'name', 'address']

class EmployeeAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAvailability
        fields = ['id', 'date', 'is_available']

class EmployeeSerializer(serializers.ModelSerializer):
    availability = EmployeeAvailabilitySerializer(many=True, read_only=True)
    is_available_on_date = serializers.SerializerMethodField()

    class Meta:
        # Tell the serializer which model it represents.
        model = Employee
        # List the fields you want to include.
        fields = ['id', 'name', 'phone_number', 'address', 'unavailable_days', 'availability', 'locations', 'is_available_on_date']

    def get_is_available_on_date(self, obj):
        date_str = self.context.get('date')
        if not date_str:
            return None

        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            # First, check for a specific availability entry
            avail = EmployeeAvailability.objects.get(employee=obj, date=date_obj)
            return avail.is_available
        except EmployeeAvailability.DoesNotExist:
            # If no specific entry, check recurring unavailability
            day_of_week = date_obj.weekday()  # Monday is 0, Sunday is 6
            unavailable_days_str = obj.unavailable_days
            if unavailable_days_str:
                unavailable_days = [int(d) for d in unavailable_days_str.split(',') if d]
                if day_of_week in unavailable_days:
                    return False
            # If no rule says otherwise, they are available
            return True

class ShiftSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)

    class Meta:
        # Tell the serializer which model it represents.
        model = Shift
        # List the fields you want to include.
        fields = ['id', 'employee', 'employee_name', 'location', 'location_name', 'date', 'start_time', 'end_time']

class ShiftWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['employee', 'location', 'date', 'start_time', 'end_time']
        extra_kwargs = {
            'end_time': {'required': False},
        }