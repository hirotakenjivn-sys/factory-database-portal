<template>
  <div class="login-container">
    <div class="login-card card">
      <h1 class="login-title">工場データベースポータル</h1>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label class="form-label">ユーザー名</label>
          <input
            v-model="username"
            type="text"
            class="form-input"
            placeholder="ユーザー名を入力"
            required
          />
        </div>
        <div class="form-group">
          <label class="form-label">パスワード</label>
          <input
            v-model="password"
            type="password"
            class="form-input"
            placeholder="パスワードを入力"
            required
          />
        </div>
        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          <span v-if="loading" class="loading-spinner"></span>
          <span v-else>ログイン</span>
        </button>
      </form>
      <p class="login-hint">デフォルト: ユーザー名=admin, パスワード=admin123</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const success = await authStore.login(username.value, password.value)
    if (success) {
      router.push('/dashboard')
    } else {
      error.value = 'ユーザー名またはパスワードが無効です'
    }
  } catch (e) {
    error.value = 'ログインに失敗しました。もう一度お試しください。'
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
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-2xl);
}

.login-title {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
  font-size: var(--font-size-2xl);
  color: var(--text-primary);
}

.login-form {
  margin-bottom: var(--spacing-md);
}

.btn-block {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-sm);
}

.login-hint {
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}
</style>
