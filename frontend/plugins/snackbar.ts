import Vue from 'vue'
import { Store } from 'vuex'

interface SnackbarOptions {
  text: string
  color?: string
  timeout?: number
}

declare module 'vue/types/vue' {
  interface Vue {
    $snackbar: {
      success(text: string): void
      error(text: string): void
      show(options: SnackbarOptions): void
    }
  }
}

export default ({ store }: { store: Store<any> }): void => {
  Vue.prototype.$snackbar = {
    success(text: string) {
      store.dispatch('snackbar/show', {
        text,
        color: 'success'
      })
    },
    error(text: string) {
      store.dispatch('snackbar/show', {
        text,
        color: 'error'
      })
    },
    show(options: SnackbarOptions) {
      store.dispatch('snackbar/show', options)
    }
  }
} 