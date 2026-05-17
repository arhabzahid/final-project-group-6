<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const appointments = ref<any[]>([])
const user = JSON.parse(localStorage.getItem('user') || '{}')
const welcomeName = user.full_name || user.username || 'User'
const darkMode = ref(localStorage.getItem('darkMode') === 'true')
const showProfile = ref(false)
const providerAvailabilities = ref<any[]>([])
const selectedAvailability = ref<string | null>(null)
const selectedProvider = ref<number | null>(null)
const providers = ref<any[]>([])
const profile = ref({
  first_name: '',
  last_name: '',
  email: '',
  username: '',
  password: '',
  phone: ''
})

function toggleDarkMode() {
  darkMode.value = !darkMode.value
  localStorage.setItem(
    'darkMode',
    darkMode.value.toString()
  )
}

async function fetchAppointments() {
  const userId = localStorage.getItem('user_id')
  const patientId = localStorage.getItem('patient_id')

  const response = await fetch(
    `http://127.0.0.1:8000/patient-appointments/${userId}/`
  )

  appointments.value = await response.json()
}
async function cancelBooking(id: number) {
  await fetch(`http://127.0.0.1:8000/appointments/delete/${id}/`, {
    method: 'DELETE'
  })

  await fetchAppointments()

  if (selectedProvider.value) {
    await fetchProviderAvailability(selectedProvider.value)
  }

  alert('Booking cancelled successfully.')
}

function logout() {
  localStorage.removeItem('user')
  localStorage.removeItem('role')
  localStorage.removeItem('user_id')
  localStorage.removeItem('provider_id')
  router.push('/login')
}

async function fetchProviderAvailability(providerId: number) 
{
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

async function fetchProviders() {

  const response = await fetch(
    'http://127.0.0.1:8000/providers/'
  )

  providers.value = await response.json()
}

async function bookAppointment() 
{
  const userId = localStorage.getItem('user_id')
  if (!selectedAvailability.value) 
  {
    alert('Please select an availability slot.')
    return
  }
  const selectedSlot = providerAvailabilities.value.find(
    (slot: any) =>
      slot.slot_id === selectedAvailability.value
  )
  if (!selectedSlot) 
  {
    alert('Invalid availability selected.')
    return
  }
  const response = await fetch(
    'http://127.0.0.1:8000/appointments/',
    {
      method: 'POST',
      headers: 
      {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        availability: selectedSlot.availability_id,
        patient: Number(localStorage.getItem('patient_id')),
        provider: selectedSlot.provider,
        start_time: selectedSlot.start_time,
        end_time: selectedSlot.end_time,
        status: 'scheduled'
      })
    }
  )
  const data = await response.json()
  if (!response.ok) 
  {
    alert(data.error || JSON.stringify(data))
    return
  }
  alert('Appointment booked successfully!')
  fetchAppointments()
  fetchProviderAvailability(selectedProvider.value!)
  selectedAvailability.value = null
}

async function updateProfile() {
  const userId = localStorage.getItem('user_id')

  const response = await fetch(
    `http://127.0.0.1:8000/update-patient-profile/${userId}/`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        first_name: profile.value.first_name,
        last_name: profile.value.last_name,
        email: profile.value.email,
        username: profile.value.username,
        password: profile.value.password,
        patient_phone_number: profile.value.phone
      })
    }
  )

  const data = await response.json()

  if (!response.ok) {
    alert(data.error || 'Failed to update profile')
    return
  }

  alert('Profile updated successfully!')
  showProfile.value = false
}

onMounted(() => {
  fetchAppointments()
  fetchProviders()
})
</script>

<template>
  <div :class="['page', { dark: darkMode }]">
    <aside class="sidebar">
      <h2>MedCare</h2>
      <p>Patient Dashboard</p>
    </aside>

    <main class="main">
      <header class="topbar">
        <div>
          <h1>My Appointments</h1>
          <p>Welcome, {{ welcomeName }}</p>
          <p>View your scheduled hospital appointments.</p>
        </div>

        <div class="topbar-actions">
        <button
        class="refresh"
        @click="showProfile = !showProfile"
        >
        Profile
        </button>
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
<section
  v-if="showProfile"
  class="panel"
>
  <h2>Update My Profile</h2>

  <div class="form-grid">
    <input
      v-model="profile.first_name"
      placeholder="First Name"
    />

    <input
      v-model="profile.last_name"
      placeholder="Last Name"
    />

    <input
      v-model="profile.email"
      placeholder="Email"
    />

    <input
      v-model="profile.username"
      placeholder="Username"
    />

    <input
      v-model="profile.password"
      type="password"
      placeholder="New Password (optional)"
    />

    <input
      v-model="profile.phone"
      placeholder="Phone Number"
    />
  </div>

  <button
    class="refresh"
    @click="updateProfile"
  >
    Update Profile
  </button>
</section>
      <section class="stats">
        <div class="stat-card">
          <span>My Appointments</span>
          <h2>{{ appointments.length }}</h2>
        </div>
      </section>

      <section class="panel">
        <h2>Book Appointment</h2>

        <div class="form-grid">

            <select
              v-model="selectedProvider"
              @change="fetchProviderAvailability(selectedProvider)"
            >
            <option :value="null">
              Select Provider
            </option>

            <option
              v-for="provider in providers"
              :key="provider.id"
              :value="provider.id"
            >
              {{ provider.first_name }} {{ provider.last_name }}
            </option>
          </select>

          <select v-model="selectedAvailability">

            <option :value="null">
              Select Availability
            </option>

            <option
              v-for="slot in providerAvailabilities"
              :key="slot.slot_id"
              :value="slot.slot_id"
            >
              {{ new Date(slot.start_time).toLocaleDateString() }}
              {{ new Date(slot.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
              -
              {{ new Date(slot.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
            </option>

          </select>

        </div>

        <button 
          class="refresh"
          @click="bookAppointment"
        >

          Book Appointment
        </button>
      </section>

      <section class="panel">
        <h2>Appointment List</h2>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Provider</th>
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
              {{ appointment.provider }} - {{ appointment.provider_name }}
              </td>
              <td>
              <span :class="['status', appointment.status]">
              {{ appointment.status }}
              </span>
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
              <button
              v-if="appointment.status === 'scheduled'"
              class="cancel"
              @click="cancelBooking(appointment.appointment_id)"
              >
              Cancel
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
  margin-bottom: 25px;
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
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}
input,
select {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
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
.cancel {
  background: #dc2626;
  color: white;
  border: none;
  padding: 8px 13px;
  border-radius: 8px;
  cursor: pointer;
}
</style>
