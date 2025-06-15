import { RuleApplicationService } from '@/services/application/rule/ruleApplicationService'
import type { RuleDTO, VoteResultDTO } from '@/repositories/rule/apiRuleRepository'

const service = new RuleApplicationService()

export function useRuleVoting() {
  // Função para buscar as regras de um projeto específico
  // Retorna uma lista de regras (RuleDTO) para o projeto

  async function fetchRules(projectId: number): Promise<RuleDTO[]> {
    const resp = await service.fetchRules(projectId)
    // resp é { count, next, previous, results: RuleDTO[] }
    return (resp as any).results
  }

  const voteRule = (
    projectId: number,
    votes: { rule_id: number; vote: boolean }[]
  ): Promise<VoteResultDTO> => {
    return service.voteRule(projectId, votes)
  }

  return { fetchRules, voteRule }
}