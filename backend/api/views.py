from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Patient, Provider, Appointment, Availability 
from .serializers import PatientSerializer, ProviderSerializer, AppointmentSerializer, AvailabilitySerializer



@api_view(['GET'])
def health(request):
    return Response({"status": "API working"})


@api_view(['GET'])
def home(request):
    return Response({"message": "Backend running"})


@api_view(['GET', 'POST'])
def patients(request):
    if request.method == 'GET':
        data = Patient.objects.all()
        serializer = PatientSerializer(data, many=True)
        return Response(serializer.data)

    serializer = PatientSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['GET', 'POST'])
def providers(request):
    if request.method == 'GET':
        data = Provider.objects.all()
        serializer = ProviderSerializer(data, many=True)
        return Response(serializer.data)

    serializer = ProviderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['GET', 'POST'])
def appointments(request):
    if request.method == 'GET':
        data = Appointment.objects.all()
        serializer = AppointmentSerializer(data, many=True)
        return Response(serializer.data)

    serializer = AppointmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['DELETE'])
def delete_appointment(request, id):
    try:
        appt = Appointment.objects.get(appointment_id=id)
        appt.delete()
        return Response({"message": "Deleted"})
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"})

@api_view(['GET', 'POST'])
def availability(request):
    if request.method == 'GET':
        data = Availability.objects.all()
        serializer = AvailabilitySerializer(data, many=True)
        return Response(serializer.data)

    serializer = AvailabilitySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['PUT'])
def update_appointment(request, id):
    try:
        appt = Appointment.objects.get(appointment_id=id)
    except Appointment.DoesNotExist:
        return Response({"error": "Appointment not found"})

    serializer = AppointmentSerializer(appt, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors)
