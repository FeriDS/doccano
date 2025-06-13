export const state = () => ({
  username: null,
  id: null,
  isAuthenticated: false,
  isStaff: false
})

export const mutations = {
  setAuthenticated(state, isAuthenticated) {
    state.isAuthenticated = isAuthenticated
  },
  setUsername(state, username) {
    state.username = username
  },
  setUserId(state, id) {
    state.id = id
  },
  setIsStaff(state, isStaff) {
    state.isStaff = isStaff
  },
  clearUsername(state) {
    state.username = null
  }
}

export const getters = {
  isAuthenticated: state => state.isAuthenticated,
  getUsername: state => state.username,
  getUserId: state => state.id,
  isStaff: state => state.isStaff
}

export const actions = {
  async authenticateUser({ commit }, authData) {
    try {
      const response = await this.$repositories.auth.login(authData.username, authData.password)
      if (response && response.data && response.data.key) {
        localStorage.setItem('token', response.data.key)
        commit('setAuthenticated', true)
      } else {
        throw new Error('Token não recebido')
      }
    } catch (error) {
      throw new Error('Credenciais inválidas')
    }
  },
  async fetchSocialLink() {
    return await this.$repositories.auth.socialLink()
  },
  async initAuth({ commit }) {
    try {
      const user = await this.$repositories.user.getProfile()
      commit('setAuthenticated', true)
      commit('setUsername', user.username)
      commit('setUserId', user.id)
      commit('setIsStaff', user.isStaff)
    } catch {
      commit('setAuthenticated', false)
      commit('setIsStaff', false)
      localStorage.removeItem('token')
    }
  },
  async logout({ commit }) {
    await this.$repositories.auth.logout()
    commit('setAuthenticated', false)
    commit('setIsStaff', false)
    commit('clearUsername')
    localStorage.removeItem('token')
  }
}
