from rest_framework import serializers
from .models import Patient, Provider, Availability, Appointment
class patientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '_all_';
class providerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '_all_';
class availabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        field = '_all_';
class appointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '_all_';



