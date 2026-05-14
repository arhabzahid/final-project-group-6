<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const appointments = ref<any[]>([])
const user = JSON.parse(localStorage.getItem('user') || '{}')
const welcomeName = user.full_name || user.username || 'User'
const darkMode = ref(false)

function toggleDarkMode() {
  darkMode.value = !darkMode.value
}

async function fetchAppointments() {
  const userId = localStorage.getItem('user_id')

  const response = await fetch(
    `http://127.0.0.1:8000/patient-appointments/${userId}/`
  )

  appointments.value = await response.json()
}

function logout() {
  localStorage.removeItem('user')
  localStorage.removeItem('role')
  localStorage.removeItem('user_id')
  localStorage.removeItem('provider_id')
  router.push('/login')
}

onMounted(() => {
  fetchAppointments()
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
        <h2>Appointment List</h2>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Provider</th>
              <th>Status</th>
              <th>Start Time</th>
              <th>End Time</th>
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
              <span class="status">{{ appointment.status }}</span>
              </td>
              <td>{{ appointment.start_time }}</td>
              <td>{{ appointment.end_time }}</td>
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
</style>
