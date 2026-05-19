from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from unittest.mock import patch
from .models import Patient, Provider, Availability, Appointment
from django.utils import timezone
from datetime import timedelta


# Patch target for all tests that trigger email
MOCK_EMAIL = 'api.views.send_appointment_email'


def make_patient_user(username='patient1', password='pass123'):
    user = User.objects.create_user(username=username, password=password)
    patient = Patient.objects.create(user=user)
    return user, patient


def make_provider_user(username='provider1', password='pass123'):
    user = User.objects.create_user(username=username, password=password)
    provider = Provider.objects.create(user=user)
    return user, provider


def make_availability(provider, hours_from_now=2, duration_hours=2, status='available'):
    start = timezone.now() + timedelta(hours=hours_from_now)
    end = start + timedelta(hours=duration_hours)
    return Availability.objects.create(
        provider=provider,
        start_time=start,
        end_time=end,
        status=status
    )


def make_appointment(patient, provider, availability=None, hours_from_now=2, duration_minutes=30):
    start = timezone.now() + timedelta(hours=hours_from_now)
    end = start + timedelta(minutes=duration_minutes)
    return Appointment.objects.create(
        availability=availability,
        patient=patient,
        provider=provider,
        start_time=start,
        end_time=end,
        status='scheduled'
    )


# ──────────────────────────────────────────────
# AUTH TESTS
# ──────────────────────────────────────────────

class LoginTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.patient = Patient.objects.create(user=self.user)

    def test_login_success_returns_patient_role(self):
        res = self.client.post('/login/', {'username': 'testuser', 'password': 'pass123'}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['role'], 'patient')

    def test_login_returns_patient_id(self):
        res = self.client.post('/login/', {'username': 'testuser', 'password': 'pass123'}, format='json')
        self.assertEqual(res.data['patient_id'], self.patient.id)

    def test_login_wrong_password_returns_401(self):
        res = self.client.post('/login/', {'username': 'testuser', 'password': 'wrong'}, format='json')
        self.assertEqual(res.status_code, 401)
        self.assertFalse(res.data['success'])

    def test_login_nonexistent_user_returns_401(self):
        res = self.client.post('/login/', {'username': 'nobody', 'password': 'pass123'}, format='json')
        self.assertEqual(res.status_code, 401)

    def test_login_provider_returns_provider_role_and_provider_id(self):
        _, provider = make_provider_user(username='prov1')
        res = self.client.post('/login/', {'username': 'prov1', 'password': 'pass123'}, format='json')
        self.assertEqual(res.data['role'], 'provider')
        self.assertEqual(res.data['provider_id'], provider.id)

    def test_login_admin_user_returns_admin_role(self):
        # A user with no Patient or Provider record is treated as admin
        User.objects.create_user(username='adminuser', password='pass123')
        res = self.client.post('/login/', {'username': 'adminuser', 'password': 'pass123'}, format='json')
        self.assertEqual(res.data['role'], 'admin')
        self.assertIsNone(res.data['provider_id'])
        self.assertIsNone(res.data['patient_id'])


class RegisterTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_register_patient_success(self):
        res = self.client.post('/api/register/', {
            'username': 'newpatient',
            'password': 'pass123',
            'email': 'p@test.com',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'role': 'patient'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['role'], 'patient')
        self.assertTrue(Patient.objects.filter(user__username='newpatient').exists())

    def test_register_provider_success(self):
        res = self.client.post('/api/register/', {
            'username': 'newprovider',
            'password': 'pass123',
            'role': 'provider'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Provider.objects.filter(user__username='newprovider').exists())

    def test_register_duplicate_username_returns_400(self):
        User.objects.create_user(username='taken', password='pass123')
        res = self.client.post('/api/register/', {
            'username': 'taken',
            'password': 'pass123',
            'role': 'patient'
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('already exists', res.data['error'])

    def test_register_missing_username_returns_400(self):
        res = self.client.post('/api/register/', {
            'username': '',
            'password': 'pass123',
            'role': 'patient'
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_register_missing_password_returns_400(self):
        res = self.client.post('/api/register/', {
            'username': 'someone',
            'password': '',
            'role': 'patient'
        }, format='json')
        self.assertEqual(res.status_code, 400)

    def test_register_invalid_role_returns_400(self):
        res = self.client.post('/api/register/', {
            'username': 'hacker',
            'password': 'pass123',
            'role': 'admin'
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('Invalid role', res.data['error'])


# ──────────────────────────────────────────────
# PATIENT TESTS
# ──────────────────────────────────────────────

class PatientTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user, self.patient = make_patient_user()

    def test_get_all_patients(self):
        res = self.client.get('/patients/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_delete_patient_success(self):
        res = self.client.delete(f'/patients/delete/{self.patient.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Patient.objects.filter(id=self.patient.id).exists())

    def test_delete_patient_also_deletes_user(self):
        user_id = self.user.id
        self.client.delete(f'/patients/delete/{self.patient.id}/')
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_delete_nonexistent_patient_returns_404(self):
        res = self.client.delete('/patients/delete/9999/')
        self.assertEqual(res.status_code, 404)

    def test_update_patient_success(self):
        res = self.client.put(f'/patients/update/{self.patient.id}/', {
            'first_name': 'Updated',
            'last_name': 'Name',
            'patient_phone_number': '555-1234'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_update_nonexistent_patient_returns_404(self):
        res = self.client.put('/patients/update/9999/', {'first_name': 'X'}, format='json')
        self.assertEqual(res.status_code, 404)

    def test_get_patient_appointments(self):
        _, provider = make_provider_user()
        avail = make_availability(provider)
        make_appointment(self.patient, provider, avail)
        res = self.client.get(f'/patient-appointments/{self.user.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_get_patient_appointments_wrong_user_returns_404(self):
        res = self.client.get('/patient-appointments/9999/')
        self.assertEqual(res.status_code, 404)


class UpdatePatientProfileTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user, self.patient = make_patient_user()

    def test_update_patient_profile_name_and_email(self):
        res = self.client.put(f'/update-patient-profile/{self.user.id}/', {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jane')
        self.assertEqual(self.user.email, 'jane@example.com')

    def test_update_patient_profile_phone(self):
        res = self.client.put(f'/update-patient-profile/{self.user.id}/', {
            'patient_phone_number': '555-0001'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.patient_phone_number, '555-0001')

    def test_update_patient_profile_password(self):
        res = self.client.put(f'/update-patient-profile/{self.user.id}/', {
            'password': 'newpass456'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass456'))

    def test_update_patient_profile_nonexistent_returns_404(self):
        res = self.client.put('/update-patient-profile/9999/', {'first_name': 'X'}, format='json')
        self.assertEqual(res.status_code, 404)


# ──────────────────────────────────────────────
# PROVIDER TESTS
# ──────────────────────────────────────────────

class ProviderTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user, self.provider = make_provider_user()

    def test_get_all_providers(self):
        res = self.client.get('/providers/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_delete_provider_success(self):
        res = self.client.delete(f'/providers/delete/{self.provider.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Provider.objects.filter(id=self.provider.id).exists())

    def test_delete_provider_also_deletes_user(self):
        user_id = self.user.id
        self.client.delete(f'/providers/delete/{self.provider.id}/')
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_delete_nonexistent_provider_returns_404(self):
        res = self.client.delete('/providers/delete/9999/')
        self.assertEqual(res.status_code, 404)

    def test_update_provider_success(self):
        res = self.client.put(f'/providers/update/{self.provider.id}/', {
            'first_name': 'Dr',
            'last_name': 'Smith',
            'specialty': 'Cardiology',
            'department': 'Heart',
            'provider_phone_number': '555-9999'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Dr')

    def test_update_nonexistent_provider_returns_404(self):
        res = self.client.put('/providers/update/9999/', {'specialty': 'X'}, format='json')
        self.assertEqual(res.status_code, 404)

    def test_get_provider_appointments(self):
        _, patient = make_patient_user()
        avail = make_availability(self.provider)
        make_appointment(patient, self.provider, avail)
        res = self.client.get(f'/provider-appointments/{self.user.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_get_provider_appointments_wrong_user_returns_404(self):
        res = self.client.get('/provider-appointments/9999/')
        self.assertEqual(res.status_code, 404)


class UpdateProviderProfileTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user, self.provider = make_provider_user()

    def test_update_provider_profile_name_and_email(self):
        res = self.client.put(f'/update-provider-profile/{self.user.id}/', {
            'first_name': 'Dr',
            'last_name': 'Jones',
            'email': 'drjones@hospital.com'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, 'Jones')
        self.assertEqual(self.user.email, 'drjones@hospital.com')

    def test_update_provider_profile_phone(self):
        res = self.client.put(f'/update-provider-profile/{self.user.id}/', {
            'provider_phone_number': '555-8888'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.provider_phone_number, '555-8888')

    def test_update_provider_profile_password(self):
        res = self.client.put(f'/update-provider-profile/{self.user.id}/', {
            'password': 'newpass789'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass789'))

    def test_update_provider_profile_nonexistent_returns_404(self):
        res = self.client.put('/update-provider-profile/9999/', {'first_name': 'X'}, format='json')
        self.assertEqual(res.status_code, 404)


# ──────────────────────────────────────────────
# AVAILABILITY TESTS
# ──────────────────────────────────────────────

class AvailabilityTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        _, self.provider = make_provider_user()
        self.start = timezone.now() + timedelta(hours=2)
        self.end = self.start + timedelta(hours=2)

    def test_create_availability_success(self):
        res = self.client.post('/availability/', {
            'provider': self.provider.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'available'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Availability.objects.count(), 1)

    def test_create_availability_end_before_start_returns_400(self):
        res = self.client.post('/availability/', {
            'provider': self.provider.id,
            'start_time': self.end.isoformat(),
            'end_time': self.start.isoformat(),
            'status': 'available'
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('End time must be after start time', res.data['error'])

    def test_create_overlapping_availability_returns_400(self):
        make_availability(self.provider, hours_from_now=2, duration_hours=2)
        overlap_start = timezone.now() + timedelta(hours=3)
        overlap_end = overlap_start + timedelta(hours=1)
        res = self.client.post('/availability/', {
            'provider': self.provider.id,
            'start_time': overlap_start.isoformat(),
            'end_time': overlap_end.isoformat(),
            'status': 'available'
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('overlaps', res.data['error'])

    def test_get_all_availability(self):
        make_availability(self.provider)
        res = self.client.get('/availability/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_delete_availability_success(self):
        avail = make_availability(self.provider)
        res = self.client.delete(f'/availability/delete/{avail.availability_id}/')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Availability.objects.filter(availability_id=avail.availability_id).exists())

    def test_delete_nonexistent_availability_returns_404(self):
        res = self.client.delete('/availability/delete/9999/')
        self.assertEqual(res.status_code, 404)


# ──────────────────────────────────────────────
# APPOINTMENT TESTS
# ──────────────────────────────────────────────

class AppointmentTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        _, self.patient = make_patient_user()
        _, self.provider = make_provider_user()
        self.avail = make_availability(self.provider, hours_from_now=2, duration_hours=4)
        self.start = timezone.now() + timedelta(hours=2)
        self.end = self.start + timedelta(minutes=30)

    @patch(MOCK_EMAIL)
    def test_create_appointment_success(self, _):
        res = self.client.post('/appointments/', {
            'availability': self.avail.availability_id,
            'patient': self.patient.id,
            'provider': self.provider.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 1)

    @patch(MOCK_EMAIL)
    def test_create_appointment_sends_email(self, mock_email):
        self.client.post('/appointments/', {
            'availability': self.avail.availability_id,
            'patient': self.patient.id,
            'provider': self.provider.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertTrue(mock_email.called)

    @patch(MOCK_EMAIL)
    def test_create_appointment_without_availability_succeeds(self, _):
        # availability is now optional (nullable)
        res = self.client.post('/appointments/', {
            'patient': self.patient.id,
            'provider': self.provider.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertEqual(res.status_code, 200)

    @patch(MOCK_EMAIL)
    def test_create_appointment_provider_conflict_returns_400(self, _):
        make_appointment(self.patient, self.provider, self.avail, hours_from_now=2)
        _, patient2 = make_patient_user(username='patient2')
        res = self.client.post('/appointments/', {
            'availability': self.avail.availability_id,
            'patient': patient2.id,
            'provider': self.provider.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('provider is already booked', res.data['error'])

    @patch(MOCK_EMAIL)
    def test_create_appointment_patient_conflict_returns_400(self, _):
        _, provider2 = make_provider_user(username='provider2')
        avail2 = make_availability(provider2, hours_from_now=2, duration_hours=4)
        make_appointment(self.patient, self.provider, self.avail, hours_from_now=2)
        res = self.client.post('/appointments/', {
            'availability': avail2.availability_id,
            'patient': self.patient.id,
            'provider': provider2.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('patient already has an appointment', res.data['error'])

    @patch(MOCK_EMAIL)
    def test_create_appointment_outside_availability_returns_400(self, _):
        outside_start = timezone.now() + timedelta(hours=10)
        outside_end = outside_start + timedelta(minutes=30)
        res = self.client.post('/appointments/', {
            'availability': self.avail.availability_id,
            'patient': self.patient.id,
            'provider': self.provider.id,
            'start_time': outside_start.isoformat(),
            'end_time': outside_end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('not available', res.data['error'])

    def test_get_all_appointments(self):
        make_appointment(self.patient, self.provider, self.avail)
        res = self.client.get('/appointments/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    @patch(MOCK_EMAIL)
    def test_delete_appointment_success(self, _):
        appt = make_appointment(self.patient, self.provider, self.avail)
        res = self.client.delete(f'/appointments/delete/{appt.appointment_id}/')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Appointment.objects.filter(appointment_id=appt.appointment_id).exists())

    @patch(MOCK_EMAIL)
    def test_delete_appointment_restores_availability_status(self, _):
        self.avail.status = 'booked'
        self.avail.save()
        appt = make_appointment(self.patient, self.provider, self.avail)
        self.client.delete(f'/appointments/delete/{appt.appointment_id}/')
        self.avail.refresh_from_db()
        self.assertEqual(self.avail.status, 'available')

    @patch(MOCK_EMAIL)
    def test_delete_appointment_sends_email(self, mock_email):
        appt = make_appointment(self.patient, self.provider, self.avail)
        self.client.delete(f'/appointments/delete/{appt.appointment_id}/')
        self.assertTrue(mock_email.called)

    def test_delete_nonexistent_appointment_returns_404(self):
        res = self.client.delete('/appointments/delete/9999/')
        self.assertEqual(res.status_code, 404)

    @patch(MOCK_EMAIL)
    def test_update_appointment_success(self, _):
        appt = make_appointment(self.patient, self.provider, self.avail, hours_from_now=2)
        new_start = timezone.now() + timedelta(hours=3)
        new_end = new_start + timedelta(minutes=30)
        res = self.client.put(f'/appointments/update/{appt.appointment_id}/', {
            'availability': self.avail.availability_id,
            'patient': self.patient.id,
            'provider': self.provider.id,
            'start_time': new_start.isoformat(),
            'end_time': new_end.isoformat(),
            'status': 'completed'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'completed')

    @patch(MOCK_EMAIL)
    def test_update_appointment_sends_email(self, mock_email):
        appt = make_appointment(self.patient, self.provider, self.avail, hours_from_now=2)
        new_start = timezone.now() + timedelta(hours=3)
        new_end = new_start + timedelta(minutes=30)
        self.client.put(f'/appointments/update/{appt.appointment_id}/', {
            'availability': self.avail.availability_id,
            'patient': self.patient.id,
            'provider': self.provider.id,
            'start_time': new_start.isoformat(),
            'end_time': new_end.isoformat(),
            'status': 'completed'
        }, format='json')
        self.assertTrue(mock_email.called)

    def test_update_nonexistent_appointment_returns_error(self):
        res = self.client.put('/appointments/update/9999/', {
            'availability': self.avail.availability_id,
            'patient': self.patient.id,
            'provider': self.provider.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertIn('error', res.data)


# ──────────────────────────────────────────────
# PROVIDER CREATE APPOINTMENT TESTS
# ──────────────────────────────────────────────

class ProviderCreateAppointmentTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.puser, self.provider = make_provider_user()
        _, self.patient = make_patient_user()
        self.avail = make_availability(self.provider, hours_from_now=2, duration_hours=4)
        self.start = timezone.now() + timedelta(hours=2)
        self.end = self.start + timedelta(minutes=30)

    @patch(MOCK_EMAIL)
    def test_provider_create_appointment_success(self, _):
        res = self.client.post(f'/provider-create-appointment/{self.puser.id}/', {
            'availability': self.avail.availability_id,
            'patient': self.patient.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 1)

    @patch(MOCK_EMAIL)
    def test_provider_create_appointment_sends_email(self, mock_email):
        self.client.post(f'/provider-create-appointment/{self.puser.id}/', {
            'availability': self.avail.availability_id,
            'patient': self.patient.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertTrue(mock_email.called)

    def test_provider_create_appointment_invalid_user_returns_404(self):
        res = self.client.post('/provider-create-appointment/9999/', {
            'availability': self.avail.availability_id,
            'patient': self.patient.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertEqual(res.status_code, 404)

    @patch(MOCK_EMAIL)
    def test_provider_create_appointment_double_booking_returns_400(self, _):
        make_appointment(self.patient, self.provider, self.avail, hours_from_now=2)
        _, patient2 = make_patient_user(username='patient2')
        res = self.client.post(f'/provider-create-appointment/{self.puser.id}/', {
            'availability': self.avail.availability_id,
            'patient': patient2.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('already booked', res.data['error'])

    @patch(MOCK_EMAIL)
    def test_provider_create_appointment_outside_availability_returns_400(self, _):
        outside_start = timezone.now() + timedelta(hours=10)
        outside_end = outside_start + timedelta(minutes=30)
        res = self.client.post(f'/provider-create-appointment/{self.puser.id}/', {
            'availability': self.avail.availability_id,
            'patient': self.patient.id,
            'start_time': outside_start.isoformat(),
            'end_time': outside_end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('not available', res.data['error'])

    @patch(MOCK_EMAIL)
    def test_provider_create_appointment_without_availability_succeeds(self, _):
        # availability is now optional
        res = self.client.post(f'/provider-create-appointment/{self.puser.id}/', {
            'patient': self.patient.id,
            'start_time': self.start.isoformat(),
            'end_time': self.end.isoformat(),
            'status': 'scheduled'
        }, format='json')
        self.assertEqual(res.status_code, 200)
