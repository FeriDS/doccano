import ApiService from '@/services/api.service'

export class APIPerspectiveRepository {
  constructor(private readonly request = ApiService) {}

  async fetchPerspectiveFields(projectId: number): Promise<any[]> {
    const url = `/projects/${projectId}/perspective/fields/`
    const response = await this.request.get(url)
    return response.data
  }

  async submitAnswers(projectId: number, 
    answers: Record<number, string | number | boolean>): Promise<void> {
    const url = `/projects/${projectId}/perspective/answers/`
    const payload = Object.entries(answers).map(([fieldId, value]) => ({
      field_id: Number(fieldId),
      value
    }))
    await this.request.post(url, payload)
  }
}
