interface State {
  show: boolean
  text: string
  color: string
  timeout: number
}

interface ShowOptions {
  text: string
  color?: string
  timeout?: number
}

export const state = (): State => ({
  show: false,
  text: '',
  color: 'success',
  timeout: 5000
})

export const mutations = {
  SET_SHOW(state: State, value: boolean) {
    state.show = value
  },
  SET_TEXT(state: State, value: string) {
    state.text = value
  },
  SET_COLOR(state: State, value: string) {
    state.color = value
  },
  SET_TIMEOUT(state: State, value: number) {
    state.timeout = value
  }
}

export const actions = {
  show({ commit }: { commit: Function }, { text, color = 'success', timeout = 5000 }: ShowOptions) {
    commit('SET_TEXT', text)
    commit('SET_COLOR', color)
    commit('SET_TIMEOUT', timeout)
    commit('SET_SHOW', true)
  },
  hide({ commit }: { commit: Function }) {
    commit('SET_SHOW', false)
  }
} 