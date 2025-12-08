import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const login = async (username, password) => {
    try {
      // FastAPIのOAuth2形式に合わせてURLSearchParamsで送信
      const params = new URLSearchParams()
      params.append('username', username)
      params.append('password', password)

      const response = await api.post('/auth/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      token.value = response.data.access_token
      localStorage.setItem('token', token.value)

      // ユーザー情報を取得
      await fetchUser()

      return true
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (error) {
      console.error('Fetch user error:', error)
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return {
    user,
    token,
    login,
    logout,
    fetchUser,
  }
})
