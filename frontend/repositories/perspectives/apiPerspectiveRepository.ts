export class APIPerspectiveRepository {
  private get axios() {
    return (window as any).$nuxt.$axios
  }

  async list() {
    const response = await this.axios.$get('/v1/perspectives/')
    // Ensure we always return an array
    if (Array.isArray(response)) {
      return response
    } else {
      console.warn('Perspective API did not return an array, converting to array')
      return response ? [response] : []
    }
  }

  async findById(id: number) {
    return await this.axios.$get(`/v1/perspectives/${id}/`)
  }

  async getProjectPerspective(projectId: string) {
    return await this.axios.$get(`/v1/projects/${projectId}/perspective/`)
  }

  async updateProjectPerspective(projectId: string, perspectiveId: number) {
    return await this.axios.$post('/v1/project-perspectives/', {
      project: projectId,
      perspective: perspectiveId
    })
  }

  async getUserPerspectiveAnswer(projectId: string) {
    const res = await this.axios.$get(`/v1/projects/${projectId}/user-answers/`)
    return res.length > 0 ? res[0] : null
  }

  async updateUserPerspectiveAnswer(projectId: string, values: Record<string, any>) {
    return await this.axios.$patch(`/v1/projects/${projectId}/user-answers/update/`, {
      field_values: values
    })
  }

  async create(perspective: Record<string, any>) {
    return await this.axios.$post('/v1/perspectives/', perspective)
  }

  async update(perspective: Record<string, any>) {
    return await this.axios.$put(`/v1/perspectives/${perspective.id}/`, perspective)
  }

  async delete(id: number) {
    return await this.axios.$delete(`/v1/perspectives/${id}/`)
  }
}
