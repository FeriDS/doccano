import { APIPerspectiveRepository } from '@/repositories/perspective/apiPerspectiveRepository'

export class PerspectiveApplicationService {
  constructor(private readonly repository: APIPerspectiveRepository) {}

  async fetchPerspectiveFields(projectId: number): Promise<any[]> {
    return await this.repository.fetchPerspectiveFields(projectId)
  }

  async submitAnswers(projectId: number, 
    answers: Record<number, string | number | boolean>): Promise<void> {
    await this.repository.submitAnswers(projectId, answers)
  }
}
