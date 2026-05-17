<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    const res = await axios.post('http://127.0.0.1:8000/login/', {
      username: username.value,
      password: password.value,
    })

    if (res.data.success) {
      localStorage.setItem('user', JSON.stringify(res.data))
      localStorage.setItem('role', res.data.role)
      localStorage.setItem('user_id', res.data.user_id)
      localStorage.setItem('provider_id', res.data.provider_id)
      localStorage.setItem('patient_id', res.data.patient_id)

  if (res.data.role === 'admin') {
    router.push('/dashboard/admin')
  } else if (res.data.role === 'provider') {
    router.push('/dashboard/provider')
  } else {
    router.push('/dashboard/patient')
  }
    }
  } catch (err: any) {
    if (err.response?.status === 401) {
      error.value = 'Invalid username or password.'
    } else {
      error.value = 'Unable to connect to server. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <!-- Left branding panel -->
    <div class="brand-panel">
      <div class="brand-content">
        <div class="brand-logo">+</div>
        <h1>MedPortal</h1>
        <p>Secure, seamless access for patients and providers.</p>
        <ul class="brand-features">
          <li>View and manage appointments</li>
          <li>Communicate with your care team</li>
          <li>Access your health records</li>
        </ul>
      </div>
    </div>

    <!-- Right form panel -->
    <div class="form-panel">
      <div class="form-box">
        <h2>Sign In</h2>
        <p class="form-subtitle">Welcome back — enter your credentials below.</p>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="field">
            <label for="username">Username</label>
            <input
              id="username"
              v-model="username"
              type="text"
              placeholder="Enter your username"
              autocomplete="username"
              required
            />
          </div>

          <div class="field">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="Enter your password"
              autocomplete="current-password"
              required
            />
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>

          <button type="submit" :disabled="loading" class="submit-btn">
            {{ loading ? 'Signing in…' : 'Sign In' }}
          </button>
        </form>

        <p class="footer-note">
          Don't have an account?
          <router-link to="/register" class="link">Create one</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
}

/* ── Brand panel ── */
.brand-panel {
  background: linear-gradient(160deg, #0f3d6e 0%, #0f6cbd 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 4rem;
  color: #fff;
}

.brand-content {
  max-width: 420px;
}

.brand-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  font-size: 2.2rem;
  font-weight: bold;
  margin-bottom: 1.25rem;
  line-height: 1;
}

.brand-content h1 {
  font-size: 2.4rem;
  font-weight: 800;
  margin: 0 0 0.75rem;
  letter-spacing: -0.5px;
}

.brand-content > p {
  font-size: 1.05rem;
  opacity: 0.85;
  line-height: 1.6;
  margin: 0 0 2rem;
}

.brand-features {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.brand-features li {
  font-size: 0.95rem;
  opacity: 0.9;
  padding-left: 1.4rem;
  position: relative;
}

.brand-features li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #7fd4ff;
  font-weight: 700;
}

/* ── Form panel ── */
.form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f4f8fd;
  padding: 3rem 4rem;
}

.form-box {
  width: 100%;
  max-width: 420px;
}

.form-box h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f3d6e;
  margin: 0 0 0.35rem;
}

.form-subtitle {
  color: #5a7a99;
  font-size: 0.9rem;
  margin: 0 0 2rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #2c4a6b;
}

.field input {
  padding: 0.7rem 1rem;
  border: 1.5px solid #c4d9ee;
  border-radius: 8px;
  font-size: 0.95rem;
  color: #1a2e42;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}

.field input:focus {
  border-color: #0f6cbd;
  box-shadow: 0 0 0 3px rgba(15, 108, 189, 0.15);
}

.error-msg {
  background: #fff0f0;
  border: 1px solid #f5c2c2;
  color: #c0392b;
  border-radius: 7px;
  padding: 0.6rem 0.85rem;
  font-size: 0.875rem;
}

.submit-btn {
  padding: 0.8rem;
  background: #0f6cbd;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  margin-top: 0.25rem;
}

.submit-btn:hover:not(:disabled) {
  background: #0d5aa0;
}

.submit-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.footer-note {
  text-align: center;
  font-size: 0.875rem;
  color: #7a9ab8;
  margin-top: 1.75rem;
  margin-bottom: 0;
}

.link {
  color: #0f6cbd;
  font-weight: 600;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
