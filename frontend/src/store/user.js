import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

function parseUser() {
  try {
    return JSON.parse(localStorage.getItem('user') || 'null')
  } catch {
    return null
  }
}

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(parseUser())
  const isAuthenticated = computed(() => Boolean(token.value))

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setUser(newUser) {
    user.value = newUser
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  function clearAuth() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function logout() {
    clearAuth()
  }

  return { token, user, isAuthenticated, setToken, setUser, clearAuth, logout }
})
