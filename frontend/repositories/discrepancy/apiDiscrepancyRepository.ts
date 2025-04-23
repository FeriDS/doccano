import ApiService from '@/services/api.service'

export class APIDiscrepancyRepository {
  constructor(private readonly request = ApiService) {}

  async fetchExamplesWithAnnotations(projectId: number): Promise<any[]> {
    const url = `/projects/${projectId}/discrepancies/annotations/`
    const response = await this.request.get(url)
    return response.data
  }

  async markDiscrepancy(projectId: number, exampleId: number): Promise<void> {
    const url = `/projects/${projectId}/discrepancies/examples/${exampleId}/`
    await this.request.post(url)
  }
}
