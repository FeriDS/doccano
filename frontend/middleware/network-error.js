export default function ({ $axios, store }) {
    $axios.onError(error => {
      if (!error.response) {
        store.commit('setConnectionError', true)
      } else {
        store.commit('setConnectionError', false)
      }
    })
  }
  