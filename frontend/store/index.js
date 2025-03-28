export const state = () => ({
    connectionError: false
  })
  
  export const mutations = {
    setConnectionError(state, hasError) {
      state.connectionError = hasError
    }
  }
  