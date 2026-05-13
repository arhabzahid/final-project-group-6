from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import Patient, Provider, Appointment, Availability 
from .serializers import PatientSerializer, ProviderSerializer, AppointmentSerializer, AvailabilitySerializer
from django.contrib.auth.models import User

@api_view(["POST"])
def login_view(request):
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "").strip()

    user = authenticate(
        username=username,
        password=password
    )
    if user is not None:

        role = "admin"

        if Patient.objects.filter(user=user).exists():
            role = "patient"

        elif Provider.objects.filter(user=user).exists():
            role = "provider"

        return Response({
            "success": True,
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.get_full_name(),
            "role": role
        })

    return Response({
        "success": False,
        "message": "Invalid credentials"
    }, status=401)


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

    if request.method == 'POST':
        serializer = AppointmentSerializer(data=request.data)

        if serializer.is_valid():
            provider = serializer.validated_data["provider"]
            patient = serializer.validated_data["patient"]
            start_time = serializer.validated_data["start_time"]
            end_time = serializer.validated_data["end_time"]

            provider_conflict = Appointment.objects.filter(
                provider=provider,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exists()

            if provider_conflict:
                return Response(
                    {"error": "This provider is already booked during this time."},
                    status=400
                )

            patient_conflict = Appointment.objects.filter(
                patient=patient,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).exists()

            if patient_conflict:
                return Response(
                    {"error": "This patient already has an appointment during this time."},
                    status=400
                )

            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)
    
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

@api_view(["POST"])
def register_view(request):
    username = request.data.get("username", "").strip()
    password = request.data.get("password", "").strip()
    email = request.data.get("email", "").strip()
    first_name = request.data.get("first_name", "").strip()
    last_name = request.data.get("last_name", "").strip()
    role = request.data.get("role", "").strip()

    if not username or not password:
        return Response({
            "error": "Username and password are required."
        }, status=400)

    if User.objects.filter(username=username).exists():
        return Response({
            "error": "Username already exists."
        }, status=400)

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name
    )
    if role == "patient":
        Patient.objects.create(user=user)

    elif role == "provider":
        Provider.objects.create(user=user)

    else:
        return Response({"error": "Invalid role selected."}, status=400)


    return Response({
        "success": True,
        "user_id": user.id,
        "username": user.username,
        "role": role
    })
@api_view(['GET'])
def patient_appointments(request, user_id):
    try:
        patient = Patient.objects.get(user_id=user_id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=404)

    data = Appointment.objects.filter(patient=patient)
    serializer = AppointmentSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def provider_appointments(request, user_id):
    try:
        provider = Provider.objects.get(user_id=user_id)
    except Provider.DoesNotExist:
        return Response({"error": "Provider not found"}, status=404)

    data = Appointment.objects.filter(provider=provider)
    serializer = AppointmentSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
def delete_patient(request, id):
    try:
        patient = Patient.objects.get(id=id)
        patient.user.delete()
        return Response({"message": "Patient deleted"})
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=404)


@api_view(['DELETE'])
def delete_provider(request, id):
    try:
        provider = Provider.objects.get(id=id)
        provider.user.delete()
        return Response({"message": "Provider deleted"})
    except Provider.DoesNotExist:
        return Response({"error": "Provider not found"}, status=404)
@api_view(['POST'])
def provider_create_appointment(request, user_id):
    try:
        provider = Provider.objects.get(user_id=user_id)
    except Provider.DoesNotExist:
        return Response({"error": "Provider not found"}, status=404)

    data = request.data.copy()
    data["provider"] = provider.id

    serializer = AppointmentSerializer(data=data)

    if serializer.is_valid():
        patient = serializer.validated_data["patient"]
        start_time = serializer.validated_data["start_time"]
        end_time = serializer.validated_data["end_time"]

        provider_conflict = Appointment.objects.filter(
            provider=provider,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if provider_conflict:
            return Response({"error": "You are already booked during this time."}, status=400)

        patient_conflict = Appointment.objects.filter(
            patient=patient,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if patient_conflict:
            return Response({"error": "This patient already has an appointment during this time."}, status=400)

        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)
@api_view(['PUT'])
def update_patient(request, id):
    try:
        patient = Patient.objects.get(id=id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=404)

    user = patient.user
    user.first_name = request.data.get("first_name", user.first_name)
    user.last_name = request.data.get("last_name", user.last_name)
    user.save()

    patient.patient_phone_number = request.data.get("patient_phone_number", patient.patient_phone_number)
    patient.insurance_provider = request.data.get("insurance_provider", patient.insurance_provider)
    patient.medications = request.data.get("medications", patient.medications)
    patient.save()

    serializer = PatientSerializer(patient)
    return Response(serializer.data)


@api_view(['PUT'])
def update_provider(request, id):
    try:
        provider = Provider.objects.get(id=id)
    except Provider.DoesNotExist:
        return Response({"error": "Provider not found"}, status=404)

    user = provider.user
    user.first_name = request.data.get("first_name", user.first_name)
    user.last_name = request.data.get("last_name", user.last_name)
    user.save()

    provider.specialty = request.data.get("specialty", provider.specialty)
    provider.department = request.data.get("department", provider.department)
    provider.provider_phone_number = request.data.get("provider_phone_number", provider.provider_phone_number)
    provider.save()

    serializer = ProviderSerializer(provider)
    return Response(serializer.data)
