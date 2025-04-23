import { DiscrepancyApplicationService } from '@/services/application/discrepancy/discrepancyApplicationService'
import { APIDiscrepancyRepository } from '@/repositories/discrepancy/apiDiscrepancyRepository'

const service = new DiscrepancyApplicationService(new APIDiscrepancyRepository())

// Composable que será usado no componente Vue
export const useDiscrepancy = () => {
  const fetchExamplesWithAnnotations = async (projectId: number) => {
    return await service.fetchExamplesWithAnnotations(projectId)
  }

  const markDiscrepancy = async (projectId: number, exampleId: number) => {
    return await service.markDiscrepancy(projectId, exampleId)
  }

  return {
    fetchExamplesWithAnnotations,
    markDiscrepancy
  }
}
