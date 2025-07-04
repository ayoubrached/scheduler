# schedule/admin.py

from django.contrib import admin
from .models import Location, Employee, Shift

# This customizes the display for the Shift model in the admin list view
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('employee', 'location', 'date', 'start_time', 'end_time')
    list_filter = ('location', 'date', 'start_time')

admin.site.register(Location)
admin.site.register(Employee)
admin.site.register(Shift, ShiftAdmin)