import { Perspective } from '~/domain/models/perspectives/perspective'
import { APIPerspectiveRepository } from '~/repositories/perspectives/apiPerspectiveRepository'

interface State {
  perspectives: Perspective[]
  loading: boolean
  error: Error | null
}

interface Context {
  commit: Function
  dispatch: Function
  state: State
  $repositories: {
    perspective: APIPerspectiveRepository
  }
}

export const state = (): State => ({
  perspectives: [],
  loading: false,
  error: null
})

export const mutations = {
  setPerspectives(state: State, perspectives: Perspective[]) {
    state.perspectives = perspectives
  },
  setLoading(state: State, value: boolean) {
    state.loading = value
  },
  setError(state: State, error: Error | null) {
    state.error = error
  }
}

export const actions = {
  async fetchPerspectives(this: Context, { commit }: { commit: Function }): Promise<void> {
    try {
      commit('setLoading', true)
      commit('setError', null)
      const perspectives = await this.$repositories.perspective.list()
      
      // Ensure we have an array of perspectives
      if (!Array.isArray(perspectives)) {
        console.error('Perspectives data is not an array', perspectives)
        commit('setPerspectives', [])
      } else {
        commit('setPerspectives', perspectives)
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred while fetching perspectives'
      commit('setError', new Error(errorMessage))
      commit('setPerspectives', []) // Set empty array on error
      throw error
    } finally {
      commit('setLoading', false)
    }
  },

  async createPerspective(
    this: Context,
    { commit, dispatch }: { commit: Function; dispatch: Function },
    perspective: Perspective
  ): Promise<Perspective> {
    try {
      commit('setLoading', true)
      commit('setError', null)
      const newPerspective = await this.$repositories.perspective.create(perspective)
      await dispatch('fetchPerspectives')
      return newPerspective
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred while creating perspective'
      commit('setError', new Error(errorMessage))
      throw error
    } finally {
      commit('setLoading', false)
    }
  },

  async updatePerspective(
    this: Context,
    { commit, dispatch }: { commit: Function; dispatch: Function },
    perspective: Perspective
  ): Promise<Perspective> {
    try {
      commit('setLoading', true)
      commit('setError', null)
      const updatedPerspective = await this.$repositories.perspective.update(perspective)
      await dispatch('fetchPerspectives')
      return updatedPerspective
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred while updating perspective'
      commit('setError', new Error(errorMessage))
      throw error
    } finally {
      commit('setLoading', false)
    }
  },

  async deletePerspective(
    this: Context,
    { commit, dispatch }: { commit: Function; dispatch: Function },
    id: number
  ): Promise<void> {
    try {
      commit('setLoading', true)
      commit('setError', null)
      await this.$repositories.perspective.delete(id)
      await dispatch('fetchPerspectives')
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred while deleting perspective'
      commit('setError', new Error(errorMessage))
      throw error
    } finally {
      commit('setLoading', false)
    }
  }
}

export const getters = {
  allPerspectives: (state: State) => state.perspectives,
  isLoading: (state: State) => state.loading,
  hasError: (state: State) => state.error !== null,
  currentError: (state: State) => state.error
} 