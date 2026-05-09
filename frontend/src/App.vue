<script setup lang="ts">

import { ref, onMounted } from 'vue'

const appointments = ref<any[]>([])
const patients = ref<any[]>([])
const providers = ref<any[]>([])
const currentView = ref('appointments')

const newAppointment = ref({
  availability_id: 1,
  patient: 1,
  provider: 1,
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

async function addAppointment() {
  await fetch('http://127.0.0.1:8000/appointments/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
  availability_id: 1,
  patient: Number(newAppointment.value.patient),
  provider: Number(newAppointment.value.provider),
  start_time: newAppointment.value.start_time,
  end_time: newAppointment.value.end_time,
  status: "scheduled"
})
  })

  await fetchAppointments()

  newAppointment.value = {
    availability_id: 1,
    patient: 1,
    provider: 1,
    start_time: '',
    end_time: '',
    status: 'scheduled'
  }
}

async function deleteAppointment(id: number) {
  await fetch(`http://127.0.0.1:8000/appointments/delete/${id}/`, {
    method: 'DELETE'
  })

  await fetchAppointments()
}

onMounted(() => {
  fetchAppointments()
  fetchPatients()
  fetchProviders()
})
</script>

<template>
  <div class="page">
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
          <p>Manage hospital patients, providers, and appointments.</p>
        </div>

        <button class="refresh" @click="fetchAppointments">
          Refresh Data
        </button>
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
        <h2>Add Appointment</h2>

        <div class="form-grid">
          <input v-model="newAppointment.patient" placeholder="Patient ID" />
          <input v-model="newAppointment.provider" placeholder="Provider ID" />
          <input v-model="newAppointment.start_time" placeholder="Start: 2026-05-05T10:00:00Z" />
          <input v-model="newAppointment.end_time" placeholder="End: 2026-05-05T10:30:00Z" />
        </div>

        <button class="primary" @click="addAppointment">
          Add Appointment
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
              <td>{{ appointment.patient }}</td>
              <td>{{ appointment.provider }}</td>
              <td>
                <span class="status">{{ appointment.status }}</span>
              </td>
              <td>{{ appointment.start_time }}</td>
              <td>{{ appointment.end_time }}</td>
              <td>
                <button class="delete" @click="deleteAppointment(appointment.appointment_id)">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="panel" v-if="currentView === 'patients'">
        <h2>Patients</h2>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Phone</th>
              <th>Insurance</th>
              <th>Medication</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="patient in patients" :key="patient.id">
              <td>{{ patient.id }}</td>
              <td>{{ patient.patient_phone_number }}</td>
              <td>{{ patient.insurance_provider }}</td>
              <td>{{ patient.medications }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="panel" v-if="currentView === 'providers'">
        <h2>Providers</h2>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Specialty</th>
              <th>Department</th>
              <th>Phone</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="provider in providers" :key="provider.id">
              <td>{{ provider.id }}</td>
              <td>{{ provider.specialty }}</td>
              <td>{{ provider.department }}</td>
              <td>{{ provider.provider_phone_number }}</td>
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
</style>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

