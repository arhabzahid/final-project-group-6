from django.contrib import admin

# Register your models here.
from .models import Patient, Provider, Availability, Appointment

admin.site.register(Patient)
admin.site.register(Provider)
admin.site.register(Appointment)
admin.site.register(Availability)
