from rest_framework import serializers
from .models import Patient, Provider, Availability, Appointment


class PatientSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    class Meta:
        model = Patient
        fields = '__all__'


class ProviderSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    class Meta:
        model = Provider
        fields = '__all__'


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    provider_name = serializers.CharField(source='provider.user.get_full_name', read_only=True)
    class Meta:
        model = Appointment
        fields = '__all__'
    def get_patient_name(self, obj):
        name = obj.patient.user.get_full_name()
        return name if name else obj.patient.user.username
    def get_provider_name(self, obj):
        name = obj.provider.user.get_full_name()
        return name if name else obj.provider.user.username
