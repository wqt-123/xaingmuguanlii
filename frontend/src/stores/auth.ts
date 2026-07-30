import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null)
  const token = ref<string | null>(sessionStorage.getItem('atlas-token'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username: string, password: string) {
    const res: any = await authApi.login(username, password)
    if (res.code === 200) {
      token.value = res.data.access_token
      user.value = res.data.user
      sessionStorage.setItem('atlas-token', res.data.access_token)
      sessionStorage.setItem('atlas-user', JSON.stringify(res.data.user))
    }
    return res
  }

  async function fetchMe() {
    try {
      const res: any = await authApi.me()
      if (res.code === 200) user.value = res.data
    } catch { logout() }
  }

  function logout() {
    token.value = null
    user.value = null
    sessionStorage.removeItem('atlas-token')
    sessionStorage.removeItem('atlas-user')
  }

  return { user, token, isLoggedIn, isAdmin, login, fetchMe, logout }
})
