from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Employee, EmployeeAvailability, Location, Shift
from .serializers import (
    EmployeeSerializer, 
    EmployeeAvailabilitySerializer, 
    LocationSerializer, 
    ShiftSerializer,
    ShiftWriteSerializer
)
from datetime import timedelta, datetime
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, NumberFilter

class EmployeeFilter(FilterSet):
    location_id = NumberFilter(field_name='locations__id')

    class Meta:
        model = Employee
        fields = ['location_id']

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('name')
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeFilter

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['date'] = self.request.query_params.get('date', None)
        return context

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        employee = self.get_object()
        week_start_str = request.query_params.get('week_start')

        if not week_start_str:
            return Response({'error': 'week_start query parameter is required.'}, status=400)

        try:
            start_date = datetime.strptime(week_start_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        end_date = start_date + timedelta(days=6)

        employee_shifts = Shift.objects.filter(
            employee=employee,
            date__range=[start_date, end_date]
        ).order_by('date', 'start_time')

        schedule_data = []
        
        # Get all unique location/date pairs from the employee's shifts
        unique_days = employee_shifts.values('location_id', 'date').distinct()

        # Fetch all shifts for those specific days and locations in a single query
        all_shifts_for_days = Shift.objects.filter(
            location_id__in=[item['location_id'] for item in unique_days],
            date__in=[item['date'] for item in unique_days]
        ).select_related('employee', 'location')

        for shift in employee_shifts:
            colleagues = all_shifts_for_days.filter(
                location_id=shift.location_id,
                date=shift.date
            ).exclude(id=shift.id)

            schedule_data.append({
                'date': shift.date,
                'shift': ShiftSerializer(shift).data,
                'colleagues': ShiftSerializer(colleagues, many=True).data
            })

        return Response(schedule_data)


class EmployeeAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeAvailabilitySerializer

    def get_queryset(self):
        employee_id = self.kwargs.get('employee_pk')
        if employee_id:
            return EmployeeAvailability.objects.filter(employee_id=employee_id).order_by('date')
        return EmployeeAvailability.objects.none()

    def perform_create(self, serializer):
        employee_id = self.kwargs.get('employee_pk')
        employee = Employee.objects.get(id=employee_id)
        serializer.save(employee=employee)

    def list(self, request, *args, **kwargs):
        employee_id = self.kwargs.get('employee_pk')
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.now().date()
        future_date_limit = today + timedelta(days=90)

        last_availability = EmployeeAvailability.objects.filter(employee=employee).order_by('-date').first()
        start_gen_date = last_availability.date + timedelta(days=1) if last_availability else today

        if start_gen_date <= future_date_limit:
            unavailable_days_str = employee.unavailable_days or ''
            unavailable_days = [int(day) for day in unavailable_days_str.split(',') if day]
            
            records_to_create = []
            current_date = start_gen_date
            while current_date <= future_date_limit:
                is_available = current_date.weekday() not in unavailable_days
                records_to_create.append(
                    EmployeeAvailability(
                        employee=employee,
                        date=current_date,
                        is_available=is_available
                    )
                )
                current_date += timedelta(days=1)
            
            if records_to_create:
                EmployeeAvailability.objects.bulk_create(records_to_create, ignore_conflicts=True)
                
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('name')
    serializer_class = LocationSerializer

class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all().order_by('start_time')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['location', 'date', 'employee']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ShiftWriteSerializer
        return ShiftSerializer

    @action(detail=False, methods=['post'], url_path='copy-week')
    def copy_week(self, request):
        source_date_str = request.data.get('source_date')
        target_date_str = request.data.get('target_date')
        location_id = request.data.get('location_id')

        if not all([source_date_str, target_date_str, location_id]):
            return Response({'error': 'source_date, target_date, and location_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            source_start_date = datetime.strptime(source_date_str, '%Y-%m-%d').date()
            target_start_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            location = Location.objects.get(id=location_id)
        except (ValueError, Location.DoesNotExist) as e:
            return Response({'error': f'Invalid data provided: {e}'}, status=status.HTTP_400_BAD_REQUEST)

        source_end_date = source_start_date + timedelta(days=6)

        source_shifts = Shift.objects.filter(
            location=location,
            date__range=[source_start_date, source_end_date]
        )

        if not source_shifts.exists():
            return Response({'message': 'No shifts found in the source week to copy.'}, status=status.HTTP_200_OK)

        new_shifts = []
        for shift in source_shifts:
            days_diff = (shift.date - source_start_date).days
            new_date = target_start_date + timedelta(days=days_diff)

            if not Shift.objects.filter(employee=shift.employee, location=location, date=new_date).exists():
                new_shifts.append(
                    Shift(
                        employee=shift.employee,
                        location=shift.location,
                        date=new_date,
                        start_time=shift.start_time,
                        end_time=shift.end_time
                    )
                )

        if new_shifts:
            Shift.objects.bulk_create(new_shifts)
            return Response({'message': f'{len(new_shifts)} shifts copied successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'All shifts from source week already exist in the target week.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='clear-week')
    def clear_week(self, request):
        start_date_str = request.data.get('start_date')
        location_id = request.data.get('location_id')

        if not all([start_date_str, location_id]):
            return Response({'error': 'start_date and location_id are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            location = Location.objects.get(id=location_id)
        except (ValueError, Location.DoesNotExist) as e:
            return Response({'error': f'Invalid data provided: {e}'}, status=status.HTTP_400_BAD_REQUEST)

        end_date = start_date + timedelta(days=6)

        shifts_to_delete = Shift.objects.filter(
            location=location,
            date__range=[start_date, end_date]
        )

        count = shifts_to_delete.count()
        if count > 0:
            shifts_to_delete.delete()
            return Response({'message': f'{count} shifts deleted successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'No shifts to delete in the selected week.'}, status=status.HTTP_200_OK)