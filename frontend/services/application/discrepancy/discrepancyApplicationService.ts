import { APIDiscrepancyRepository } from '@/repositories/discrepancy/apiDiscrepancyRepository'

export class DiscrepancyApplicationService {
  constructor(private readonly repository: APIDiscrepancyRepository) {}

  // Buscar exemplos com anotações
  async fetchExamplesWithAnnotations(projectId: number): Promise<any[]> {
    return await this.repository.fetchExamplesWithAnnotations(projectId)
  }

  // Sinalizar discrepância
  async markDiscrepancy(projectId: number, exampleId: number): Promise<void> {
    await this.repository.markDiscrepancy(projectId, exampleId)
  }
}
