<template>
  <div class="login-container">
    <div class="login-card">
      <h2>Factory Portal Login</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="employee_no">Employee No</label>
          <input
            type="text"
            id="employee_no"
            v-model="employee_no"
            required
            placeholder="Enter your Employee No"
          />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            placeholder="Enter your password"
          />
        </div>
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const employee_no = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const formData = new FormData()
    formData.append('username', employee_no.value)
    formData.append('password', password.value)

    const response = await axios.post(`${import.meta.env.VITE_API_URL}/auth/login`, formData)
    
    const token = response.data.access_token
    localStorage.setItem('token', token)
    
    // Redirect to dashboard or previous page
    router.push('/')
  } catch (err) {
    console.error('Login error:', err)
    if (err.response && err.response.status === 401) {
      error.value = 'Invalid Employee No or Password'
    } else {
      error.value = 'An error occurred during login. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #606266;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #409eff;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #66b1ff;
}

button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.error-message {
  color: #f56c6c;
  margin-bottom: 1rem;
  text-align: center;
  font-size: 0.9rem;
}
</style>
