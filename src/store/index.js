import { createStore } from 'vuex'

export default createStore({
  state: {
    user: null,
    accessToken: localStorage.getItem('access') || null,
    refreshToken: localStorage.getItem('refresh') || null
  },
  mutations: {
    setUser(state, payload) {
      state.user = payload.user
      state.accessToken = payload.token
      state.refreshToken = payload.refreshToken
      localStorage.setItem('access', payload.token)
      localStorage.setItem('refresh', payload.refreshToken)
    },
    clearUser(state) {
      state.user = null
      state.accessToken = null
      state.refreshToken = null
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    }
  },
  getters: {
    isAuthenticated: state => !!state.accessToken,
    currentUser: state => state.user
  }
})
