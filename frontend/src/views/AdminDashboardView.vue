<script setup lang="ts">

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const appointments = ref<any[]>([])
const patients = ref<any[]>([])
const providers = ref<any[]>([])
const availability = ref<any[]>([])
const currentView = ref('appointments')
const router = useRouter()
const editingAppointmentId = ref<number | null>(null)
const user = JSON.parse(localStorage.getItem('user') || '{}')
const welcomeName = user.full_name || user.username || 'User'
const darkMode = ref(localStorage.getItem('darkMode') === 'true')
const providerAvailabilities = ref<any[]>([])
const selectedAvailability = ref<string | null>(null)

function toggleDarkMode() {
  darkMode.value = !darkMode.value
  localStorage.setItem(
    'darkMode',
    darkMode.value.toString()
  )
}

const newAppointment = ref({
  availability_id: null,
  patient: '',
  provider: '',
  start_time: '',
  end_time: '',
  status: 'scheduled'
})

async function fetchAppointments() {
  const response = await fetch('http://127.0.0.1:8000/appointments/')
  appointments.value = await response.json()
}

async function fetchPatients() {
  const response = await fetch('http://127.0.0.1:8000/patients/')
  patients.value = await response.json()
}

async function fetchProviders() {
  const response = await fetch('http://127.0.0.1:8000/providers/')
  providers.value = await response.json()
}

async function fetchAvailability() {
  const response = await fetch('http://127.0.0.1:8000/availability/')
  availability.value = await response.json()
}

async function addAppointment() {
  const selectedPatient = newAppointment.value.patient
  const selectedProvider = newAppointment.value.provider
  if (!appointmentDate.value || !appointmentTime.value) {
  alert('Please select a date and time.')
  return
  }
  if (isSunday(appointmentDate.value)) {
  alert('Appointments cannot be scheduled on Sunday.')
  return
  }
  if (isPastDate(appointmentDate.value)) {
  alert('Appointments cannot be scheduled in the past.')
  return
  }
  if (isPastDateTime(appointmentDate.value, appointmentTime.value)) {
  alert('Appointments cannot be scheduled in the past.')
  return
  }
  const selectedSlot = providerAvailabilities.value.find(
  (slot: any) => slot.slot_id === selectedAvailability.value
  )
  const availabilityId = selectedSlot
  ? selectedSlot.availability_id
  : null
  
  newAppointment.value.start_time = buildDateTime(appointmentDate.value, appointmentTime.value)
  newAppointment.value.end_time = buildEndTime(appointmentDate.value, appointmentTime.value)

  const response = await fetch('http://127.0.0.1:8000/appointments/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
  availability: availabilityId,
  patient: Number(newAppointment.value.patient),
  provider: Number(newAppointment.value.provider),
  start_time: newAppointment.value.start_time,
  end_time: newAppointment.value.end_time,
  status: newAppointment.value.status
  })
  })

  const data = await response.json()

  if (!response.ok) {
    alert(data.error || JSON.stringify(data))
    return
  }

  await fetchAppointments()

  newAppointment.value = {
    availability_id: null,
    patient: selectedPatient,
    provider: selectedProvider,
    start_time: '',
    end_time: '',
    status: 'scheduled'
  }
  appointmentDate.value = ''
  appointmentTime.value = ''
  selectedAvailability.value = null
  alert('Appointment created successfully!')
}


async function deleteAppointment(id: number) {
  await fetch(`http://127.0.0.1:8000/appointments/delete/${id}/`, {
    method: 'DELETE'
  })

  await fetchAppointments()
}
async function deletePatient(id: number) {
  await fetch(`http://127.0.0.1:8000/patients/delete/${id}/`, {
    method: 'DELETE'
  })

  await fetchPatients()
}

async function deleteProvider(id: number) {
  await fetch(`http://127.0.0.1:8000/providers/delete/${id}/`, {
    method: 'DELETE'
  })

  await fetchProviders()
}
function editPatient(patient: any) {
  editingPatientId.value = patient.id

  patientForm.value = {
    first_name: patient.first_name || '',
    last_name: patient.last_name || '',
    patient_phone_number: patient.patient_phone_number || '',
    insurance_provider: patient.insurance_provider || '',
    medications: patient.medications || ''
  }

  currentView.value = 'patients'
}

async function updatePatient() {
  const response = await fetch(
    `http://127.0.0.1:8000/patients/update/${editingPatientId.value}/`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientForm.value)
    }
  )

  if (!response.ok) {
    alert('Patient update failed.')
    return
  }

  await fetchPatients()
  editingPatientId.value = null

  alert('Patient updated successfully!')
}

function editProvider(provider: any) {
  editingProviderId.value = provider.id

  providerForm.value = {
    first_name: provider.first_name || '',
    last_name: provider.last_name || '',
    specialty: provider.specialty || '',
    department: provider.department || '',
    provider_phone_number: provider.provider_phone_number || ''
  }

  currentView.value = 'providers'
}

async function updateProvider() {
  const response = await fetch(
    `http://127.0.0.1:8000/providers/update/${editingProviderId.value}/`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(providerForm.value)
    }
  )

  if (!response.ok) {
    alert('Provider update failed.')
    return
  }

  await fetchProviders()
  editingProviderId.value = null

  alert('Provider updated successfully!')
}
function editAppointment(appointment: any) {
  editingAppointmentId.value = appointment.appointment_id

  newAppointment.value = {
    availability_id: appointment.availability,
    patient: appointment.patient,
    provider: appointment.provider,
    start_time: appointment.start_time,
    end_time: appointment.end_time,
    status: appointment.status
  }

  appointmentDate.value = appointment.start_time.split('T')[0]
  appointmentTime.value = appointment.start_time.split('T')[1].substring(0, 5)
}
const editingPatientId = ref<number | null>(null)
const editingProviderId = ref<number | null>(null)

const patientForm = ref({
  first_name: '',
  last_name: '',
  patient_phone_number: '',
  insurance_provider: '',
  medications: ''
})

const providerForm = ref({
  first_name: '',
  last_name: '',
  specialty: '',
  department: '',
  provider_phone_number: ''
})
const appointmentDate = ref('')
const appointmentTime = ref('')

const timeSlots = [
  '10:00', '10:30',
  '11:00', '11:30',
  '12:00', '12:30',
  '13:00', '13:30',
  '14:00', '14:30',
  '15:00', '15:30',
  '16:00', '16:30',
  '17:00', '17:30',
  '18:00', '18:30',
  '19:00', '19:30',
  '20:00', '20:30',
  '21:00', '21:30',
  '22:00'
]

function buildDateTime(date: string, time: string) {
  return `${date}T${time}:00Z`
}

function buildEndTime(date: string, time: string) {
  const [hour, minute] = time.split(':').map(Number)
  const start = new Date(`${date}T${time}:00Z`)
  start.setMinutes(start.getMinutes() + 30)
  return start.toISOString()
}

function isSunday(date: string) {
  const selectedDate = new Date(`${date}T00:00:00Z`)
  return selectedDate.getUTCDay() === 0
}
function isPastDate(date: string) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const selectedDate = new Date(`${date}T00:00:00`)
  selectedDate.setHours(0, 0, 0, 0)

  return selectedDate < today
}
function isPastDateTime(date: string, time: string) {
  const selectedDateTime = new Date(`${date}T${time}:00`)
  const now = new Date()

  return selectedDateTime < now
}
async function updateAppointment() {
  if (!appointmentDate.value || !appointmentTime.value) {
  alert('Please select a date and time.')
  return
  }
  if (isSunday(appointmentDate.value)) {
  alert('Appointments cannot be scheduled on Sunday.')
  return
  }
  if (isPastDate(appointmentDate.value)) {
  alert('Appointments cannot be scheduled in the past.')
  return
  }
  if (isPastDateTime(appointmentDate.value, appointmentTime.value)) {
  alert('Appointments cannot be scheduled in the past.')
  return
  }
  newAppointment.value.start_time = buildDateTime(appointmentDate.value, appointmentTime.value)
  newAppointment.value.end_time = buildEndTime(appointmentDate.value, appointmentTime.value)
  const response = await fetch(
    `http://127.0.0.1:8000/appointments/update/${editingAppointmentId.value}/`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        availability: Number(newAppointment.value.availability_id),
        patient: Number(newAppointment.value.patient),
        provider: Number(newAppointment.value.provider),
        start_time: newAppointment.value.start_time,
        end_time: newAppointment.value.end_time,
        status: newAppointment.value.status
      })
    }
  )

  const data = await response.json()

  if (!response.ok) {
    alert(data.error || JSON.stringify(data))
    return
  }

  await fetchAppointments()

  editingAppointmentId.value = null

  newAppointment.value = {
    availability_id: null,
    patient: '',
    provider: '',
    start_time: '',
    end_time: '',
    status: 'scheduled'
  }
  appointmentDate.value = ''
  appointmentTime.value = ''
  alert('Appointment updated successfully!')
}

async function selectSlot(slot: any) {
  newAppointment.value.availability_id = slot.availability_id
  newAppointment.value.start_time = slot.start_time
  newAppointment.value.end_time = slot.end_time
}

function handleAvailabilitySelection() {

  const slot = providerAvailabilities.value.find(
    (s: any) =>
      s.slot_id === selectedAvailability.value
  )

  if (!slot) return

  newAppointment.value.availability_id = slot.availability_id

  appointmentDate.value =
    slot.start_time.split('T')[0]

  appointmentTime.value =
    slot.start_time.split('T')[1].substring(0, 5)

  newAppointment.value.start_time = slot.start_time
  newAppointment.value.end_time = slot.end_time
}


async function fetchProviderAvailability(providerId: number) 
{
  selectedAvailability.value = null

  const response = await fetch
  (
    'http://127.0.0.1:8000/availability/'
  )
  const data = await response.json()

  const appointmentsResponse = await fetch(
  'http://127.0.0.1:8000/appointments/'
)

const appointments = await appointmentsResponse.json()

const availableSlots: any[] = []

const providerBlocks = data.filter(
  (slot: any) =>
    slot.provider === Number(providerId)&&
      slot.status === 'available'
)

for (const block of providerBlocks) 
{

  let current = new Date(block.start_time)
  const end = new Date(block.end_time)

  while (current < end) 
  {

    const next = new Date(current)
    next.setMinutes(next.getMinutes() + 30)

    const overlap = appointments.some((appt: any) =>
      appt.provider === Number(providerId) &&
      new Date(appt.start_time).getTime() === current.getTime()
    )

    if (!overlap) 
    {

      availableSlots.push({
        slot_id: `${block.availability_id}-${current.toISOString()}`,
        availability_id: block.availability_id,
        start_time: current.toISOString(),
        end_time: next.toISOString(),
        provider: block.provider
      })
    }

    current = next
  }
}

providerAvailabilities.value = availableSlots
}

onMounted(() => {
  fetchAppointments()
  fetchPatients()
  fetchProviders()
  fetchAvailability()
})
function logout() {
  localStorage.removeItem('user')
  localStorage.removeItem('user_id')
  localStorage.removeItem('role')
  localStorage.removeItem('provider_id')
  localStorage.removeItem('patient_id')
  router.push('/login')
}
</script>

<template>
  <div :class="['page', { dark: darkMode }]">
    <aside class="sidebar">
      <h2>MedCare</h2>
      <p>Hospital Appointment System</p>

      <button @click="currentView = 'appointments'" :class="{ active: currentView === 'appointments' }">
        Appointments
      </button>

      <button @click="currentView = 'patients'" :class="{ active: currentView === 'patients' }">
        Patients
      </button>

      <button @click="currentView = 'providers'" :class="{ active: currentView === 'providers' }">
        Providers
      </button>
    </aside>

    <main class="main">
      <header class="topbar">
        <div>
          <h1>Dashboard</h1>
          <p>Welcome, {{ welcomeName }}</p>
          <p>Manage hospital patients, providers, and appointments.</p>
        </div>

        <div class="topbar-actions">
        <button class="refresh" @click="fetchAppointments">
        Refresh Data
        </button>
        <button class="logout" @click="logout">
        Logout
        </button>
        <button class="dark-toggle" @click="toggleDarkMode">
        {{ darkMode ? 'Light Mode' : 'Dark Mode' }}
        </button>
        </div>
      </header>

      <section class="stats">
        <div class="stat-card">
          <span>Total Appointments</span>
          <h2>{{ appointments.length }}</h2>
        </div>

        <div class="stat-card">
          <span>Total Patients</span>
          <h2>{{ patients.length }}</h2>
        </div>

        <div class="stat-card">
          <span>Total Providers</span>
          <h2>{{ providers.length }}</h2>
        </div>
      </section>

      <section class="panel">
        <h2>{{ editingAppointmentId ? 'Update Appointment' : 'Add Appointment' }}</h2>

        <div class="form-grid">
          <select v-model="newAppointment.patient">
          <option disabled value="">
          Select Patient
          </option>
            <option
              v-for="patient in patients"
              :key="patient.id"
              :value="patient.id"
            >
              Patient {{ patient.id }} - {{ patient.first_name }} {{ patient.last_name}}
            </option>
          </select>
          <select 
            v-model="newAppointment.provider"
            @change="fetchProviderAvailability(newAppointment.provider)"
          >
          <option disabled value="">
          Select Provider
          </option>
            <option
              v-for="provider in providers"
              :key="provider.id"
              :value="provider.id"
            >
              Provider {{ provider.id }} - {{ provider.first_name }} {{ provider.last_name  }}
            </option>
          </select>

          <select 
            v-model="selectedAvailability"
            @change="handleAvailabilitySelection"
          >

            <option :value="null">
              Optional: Select Availability
            </option>

            <option
              v-for="slot in providerAvailabilities"
              :key="slot.slot_id"
              :value="slot.slot_id"
            >
              {{ new Date(slot.start_time).toLocaleString([], {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
                })
                }}
                -
                {{
                  new Date(slot.end_time).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                    })
                    }}
            </option>

          </select>

          <input
          v-model="appointmentDate"
          type="date"
          />
          <select v-model="appointmentTime">
          <option value="">Select Time</option>
          <option
          v-for="slot in timeSlots"
          :key="slot"
          :value="slot"
          >
          {{ slot }}
          </option>
          </select>
          <select v-if="editingAppointmentId" v-model="newAppointment.status">
          <option value="scheduled">Scheduled</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
          </select>
        </div>

        <button
        class="primary"
        @click="editingAppointmentId ? updateAppointment() : addAppointment()"
        >
        {{ editingAppointmentId ? 'Update Appointment' : 'Add Appointment' }}
        </button>
      </section>

      <section class="panel" v-if="currentView === 'appointments'">
        <h2>Appointments</h2>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Patient</th>
              <th>Provider</th>
              <th>Status</th>
              <th>Start Time</th>
              <th>End Time</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="appointment in appointments" :key="appointment.appointment_id">
              <td>{{ appointment.appointment_id }}</td>
              <td>{{ appointment.patient }} - {{ appointment.patient_name }}</td>
              <td>{{ appointment.provider }} - {{ appointment.provider_name }}</td>
              <td>
                <span :class="['status', appointment.status]">
                {{ appointment.status }}</span>
              </td>
              <td>
              {{
                new Date(appointment.start_time).toLocaleString([], {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                  })
                  }}
                  </td>
                  <td>
                  {{
                    new Date(appointment.end_time).toLocaleString([], {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                      })
                      }}
                      </td>
              <td>
                <div class="action-buttons">
                <button
                class="update"
                @click="editAppointment(appointment)"
                >
                Update
                </button>
                <button
                class="delete"
                @click="deleteAppointment(appointment.appointment_id)"
                >
                Delete
                </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="panel" v-if="currentView === 'patients'">
        <h2>Patients</h2>
        <div v-if="editingPatientId" class="form-grid">
        <input v-model="patientForm.first_name" placeholder="First Name" />
        <input v-model="patientForm.last_name" placeholder="Last Name" />
        <input v-model="patientForm.patient_phone_number" placeholder="Phone" />
        <input v-model="patientForm.insurance_provider" placeholder="Insurance" />
        <input v-model="patientForm.medications" placeholder="Medication" />
        <button class="primary" @click="updatePatient">
        Save Patient Update
        </button>
        </div>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Phone</th>
              <th>Insurance</th>
              <th>Medication</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="patient in patients" :key="patient.id">
              <td>{{ patient.id }}</td>
              <td>{{ patient.first_name }} {{ patient.last_name }}</td>
              <td>{{ patient.patient_phone_number }}</td>
              <td>{{ patient.insurance_provider }}</td>
              <td>{{ patient.medications }}</td>
              <td>
              <div class="action-buttons">
              <button class="update" @click="editPatient(patient)">
              Update
              </button>
              <button class="delete" @click="deletePatient(patient.id)">
              Delete
              </button>
              </div>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="panel" v-if="currentView === 'providers'">
        <h2>Providers</h2>
        <div v-if="editingProviderId" class="form-grid">
        <input v-model="providerForm.first_name" placeholder="First Name" />
        <input v-model="providerForm.last_name" placeholder="Last Name" />
        <input v-model="providerForm.specialty" placeholder="Specialty" />
        <input v-model="providerForm.department" placeholder="Department" />
        <input v-model="providerForm.provider_phone_number" placeholder="Phone" />
        <button class="primary" @click="updateProvider">
        Save Provider Update
        </button>
        </div>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Specialty</th>
              <th>Department</th>
              <th>Phone</th>
              <th>Action</th>
              </tr>
          </thead>

          <tbody>
            <tr v-for="provider in providers" :key="provider.id">
              <td>{{ provider.id }}</td>
              <td>{{ provider.first_name }} {{ provider.last_name }}</td>
              <td>{{ provider.specialty }}</td>
              <td>{{ provider.department }}</td>
              <td>{{ provider.provider_phone_number }}</td>
              <td>
              <div class="action-buttons">
              <button class="update" @click="editProvider(provider)">
              Update
              </button>
              <button class="delete" @click="deleteProvider(provider.id)">
              Delete
              </button>
              </div>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

.page {
  min-height: 100vh;
  display: flex;
  background: #f4f7fb;
  color: #1f2937;
  font-family: Arial, sans-serif;
}

.sidebar {
  width: 260px;
  background: #123c69;
  color: white;
  padding: 30px 20px;
}

.sidebar h2 {
  margin: 0;
  font-size: 28px;
}

.sidebar p {
  margin-bottom: 35px;
  color: #dbeafe;
  font-size: 14px;
}

.sidebar button {
  display: block;
  width: 100%;
  margin-bottom: 12px;
  padding: 13px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: white;
  text-align: left;
  cursor: pointer;
  font-size: 15px;
}

.sidebar button:hover,
.sidebar button.active {
  background: #1d5f99;
}

.main {
  flex: 1;
  padding: 30px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.topbar h1 {
  margin: 0;
  font-size: 32px;
}

.topbar p {
  margin-top: 6px;
  color: #6b7280;
}

.refresh,
.primary {
  background: #2563eb;
  color: white;
  border: none;
  padding: 12px 18px;
  border-radius: 10px;
  cursor: pointer;
}
.topbar-actions {
  display: flex;
  gap: 10px;
}

.logout {
  background: #dc2626;
  color: white;
  border: none;
  padding: 12px 18px;
  border-radius: 10px;
  cursor: pointer;
}
.action-buttons {
  display: flex;
  gap: 8px;
}

.update {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 8px 13px;
  border-radius: 8px;
  cursor: pointer;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
  margin-bottom: 25px;
}

.stat-card,
.panel {
  background: white;
  border-radius: 16px;
  padding: 22px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
}

.stat-card span {
  color: #6b7280;
}

.stat-card h2 {
  font-size: 34px;
  margin: 8px 0 0;
  color: #123c69;
}

.panel {
  margin-bottom: 25px;
}

.panel h2 {
  margin-top: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 15px;
}

input {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
}
select {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
}

table {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
}

th {
  background: #eef2ff;
  color: #374151;
  text-align: left;
  padding: 13px;
}

td {
  padding: 13px;
  border-bottom: 1px solid #e5e7eb;
}

.status {
  background: #dcfce7;
  color: #166534;
  padding: 6px 10px;
  border-radius: 20px;
  font-size: 13px;
}

.delete {
  background: #dc2626;
  color: white;
  border: none;
  padding: 8px 13px;
  border-radius: 8px;
  cursor: pointer;
}

button:hover {
  opacity: 0.9;
}

.slots {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.slots button {
  background: #e0edff;
  border: none;
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
}
.dark {
  background: #111827;
  color: #f9fafb;
}

.dark .main {
  background: #111827;
}

.dark .panel,
.dark .stat-card {
  background: #1f2937;
  color: #f9fafb;
}

.dark .topbar p,
.dark .stat-card span {
  color: #d1d5db;
}

.dark th {
  background: #374151;
  color: #f9fafb;
}

.dark td {
  border-bottom: 1px solid #374151;
}

.dark input,
.dark select {
  background: #111827;
  color: #f9fafb;
  border-color: #4b5563;
}

.dark-toggle {
  background: #111827;
  color: white;
  border: none;
  padding: 12px 18px;
  border-radius: 10px;
  cursor: pointer;
}
.dark .stat-card h2 {
  color: #93c5fd;
}
.status.scheduled {
  background: #dcfce7;
  color: #166534;
}

.status.completed {
  background: #dbeafe;
  color: #1e40af;
}

.status.cancelled {
  background: #fee2e2;
  color: #991b1b;
}
.dark input[type="date"]::-webkit-calendar-picker-indicator,
.dark input[type="datetime-local"]::-webkit-calendar-picker-indicator {
  filter: invert(1);
  cursor: pointer;
}
</style>
