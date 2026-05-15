<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const appointments = ref<any[]>([])
const patients = ref<any[]>([])

const appointmentDate = ref('')
const appointmentTime = ref('')
const editingAppointmentId = ref<number | null>(null)
const user = JSON.parse(localStorage.getItem('user') || '{}')
const welcomeName = user.full_name || user.username || 'User'
const darkMode = ref(false)
const availabilityStart = ref('')
const availabilityEnd = ref('')
const availabilities = ref<any[]>([])
const selectedAvailability = ref<number | null>(null)
const myAvailabilities = ref<any[]>([])

function toggleDarkMode() {
  darkMode.value = !darkMode.value
}

const newAppointment = ref({
  patient: 1,
  start_time: '',
  end_time: '',
  status: 'scheduled'
})

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

async function fetchAppointments() {
  const userId = localStorage.getItem('user_id')

  const response = await fetch(
    `http://127.0.0.1:8000/provider-appointments/${userId}/`
  )

  appointments.value = await response.json()
}

async function fetchPatients() {
  const response = await fetch('http://127.0.0.1:8000/patients/')
  patients.value = await response.json()
}

async function addAppointment() {
  const userId = localStorage.getItem('user_id')

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

  newAppointment.value.start_time = buildDateTime(
    appointmentDate.value,
    appointmentTime.value
  )

  newAppointment.value.end_time = buildEndTime(
    appointmentDate.value,
    appointmentTime.value
  )

  const response = await fetch(
    `http://127.0.0.1:8000/provider-create-appointment/${userId}/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        availability: selectedAvailability.value,
        patient: Number(newAppointment.value.patient),
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

  appointmentDate.value = ''
  appointmentTime.value = ''

  alert('Appointment created successfully!')
}
function editAppointment(appointment: any) {
  editingAppointmentId.value = appointment.appointment_id

  newAppointment.value = {
    patient: appointment.patient,
    start_time: appointment.start_time,
    end_time: appointment.end_time,
    status: appointment.status
  }

  appointmentDate.value = appointment.start_time.split('T')[0]
  appointmentTime.value = appointment.start_time.split('T')[1].substring(0, 5)
}
async function updateAppointment() {
  const userId = localStorage.getItem('user_id')

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

  newAppointment.value.start_time = buildDateTime(
    appointmentDate.value,
    appointmentTime.value
  )

  newAppointment.value.end_time = buildEndTime(
    appointmentDate.value,
    appointmentTime.value
  )

  const response = await fetch(
    `http://127.0.0.1:8000/appointments/update/${editingAppointmentId.value}/`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        availability: 1,
        patient: Number(newAppointment.value.patient),
        provider: Number(localStorage.getItem('provider_id') || 1),
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
  appointmentDate.value = ''
  appointmentTime.value = ''

  newAppointment.value = {
    patient: 1,
    start_time: '',
    end_time: '',
    status: 'scheduled'
  }

  alert('Appointment updated successfully!')
}
function logout() {
  localStorage.removeItem('user')
  localStorage.removeItem('role')
  localStorage.removeItem('user_id')
  localStorage.removeItem('provider_id')

  router.push('/login')
}

async function createAvailability() 
{
  const providerId = localStorage.getItem('provider_id')
  if (!availabilityStart.value || !availabilityEnd.value) 
  {
    alert('Please select availability times.')
    return
  }
  const response = await fetch
  (
    'http://127.0.0.1:8000/availability/',
    {
      method: 'POST',
      headers: 
      {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(
      {
        provider: Number(providerId),
        start_time: availabilityStart.value,
        end_time: availabilityEnd.value,
        status: 'available'
      })
    }
  )
  const data = await response.json()
  if (!response.ok) 
  {
    alert(data.error || 'Failed to create availability')
    return
  }
  alert('Availability created successfully!')
  fetchMyAvailability()
  availabilityStart.value = ''
  availabilityEnd.value = ''
}

async function fetchAvailabilities() 
{
  const response = await fetch(
    'http://127.0.0.1:8000/availability/'
  )
  const data = await response.json()
  availabilities.value = data.filter
  (
    (slot: any) => slot.status === 'available'
  )
}

async function fetchMyAvailability()
{
  const providerId = localStorage.getItem('provider_id')

  const response = await fetch(
    'http://127.0.0.1:8000/availability/'
  )

  const data = await response.json()

  myAvailabilities.value = data.filter(
    (slot: any) =>
      slot.provider === Number(providerId)
  )
}

async function deleteAvailability(id: number)
{
  await fetch(
    `http://127.0.0.1:8000/availability/delete/${id}/`,
    {
      method: 'DELETE'
    }
  )

  fetchMyAvailability()
  fetchAvailabilities()
}

onMounted(() => {
  fetchAppointments()
  fetchPatients()
  fetchAvailabilities()
  fetchMyAvailability()
})
</script>

<template>
  <div :class="['page', { dark: darkMode }]">
    <aside class="sidebar">
      <h2>MedCare</h2>
      <p>Provider Dashboard</p>
    </aside>

    <main class="main">
      <header class="topbar">
        <div>
          <h1>Provider Appointments</h1>
          <p>Welcome, {{ welcomeName }}</p>
          <p>Manage your patient appointments.</p>
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
          <span>My Appointments</span>
          <h2>{{ appointments.length }}</h2>
        </div>
      </section>

      <section class="panel">
        <h2>Create Availability</h2>
        <div class="form-grid">
          <input
            type="datetime-local"
            v-model="availabilityStart"
          />
          <input
            type="datetime-local"
            v-model="availabilityEnd"
          />
        </div>
        <button
          class="primary"
          @click="createAvailability"
        >
          Add Availability
        </button>
      </section>

      <section class="panel">
        <h2>My Availability</h2>

        <table>
          <thead>
            <tr>
              <th>Start</th>
              <th>End</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="slot in myAvailabilities"
              :key="slot.availability_id"
            >
              <td>
                {{
                  new Date(slot.start_time).toLocaleString()
                }}
              </td>

              <td>
                {{
                  new Date(slot.end_time).toLocaleString()
                }}
              </td>

              <td>
                <button
                  class="logout"
                  @click="deleteAvailability(slot.availability_id)"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="panel">
        <h2>{{ editingAppointmentId ? 'Update Appointment' : 'Create Appointment' }}</h2>

        <div class="form-grid">
          <select v-model="newAppointment.patient">
            <option
              v-for="patient in patients"
              :key="patient.id"
              :value="patient.id"
            >
              Patient {{  patient.id }} - {{ patient.first_name }} {{ patient.last_name }}
            </option>
          </select>

          <select v-model="selectedAvailability">
            <option :value="null">
              Select Availability
            </option>

            <option
              v-for="slot in availabilities"
              :key="slot.availability_id"
              :value="slot.availability_id"
            >
              Provider {{ slot.provider }} |
              {{ slot.start_time }}
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
        {{ editingAppointmentId ? 'Update Appointment' : 'Create Appointment' }}
        </button>
      </section>

      <section class="panel">
        <h2>Appointment List</h2>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Patient</th>
              <th>Status</th>
              <th>Start Time</th>
              <th>End Time</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="appointment in appointments"
              :key="appointment.appointment_id"
            >
              <td>{{ appointment.appointment_id }}</td>
              <td>
              {{ appointment.patient }} - {{ appointment.patient_name }}
              </td>

              <td>
                <span class="status">
                  {{ appointment.status }}
                </span>
              </td>

              <td>{{ appointment.start_time }}</td>
              <td>{{ appointment.end_time }}</td>
              <td>
              <button
              class="update"
              @click="editAppointment(appointment)"
              >
              Update
              </button>
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

.logout {
  background: #dc2626;
  color: white;
  border: none;
  padding: 12px 18px;
  border-radius: 10px;
  cursor: pointer;
}

.stats {
  display: grid;
  grid-template-columns: 250px;
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

table {
  width: 100%;
  border-collapse: collapse;
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
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 15px;
}

input,
select {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
}

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

.refresh {
  background: #2563eb;
  color: white;
  border: none;
  padding: 12px 18px;
  border-radius: 10px;
  cursor: pointer;
}
.update {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 8px 13px;
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
</style>
