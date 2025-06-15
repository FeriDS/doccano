import { RuleApplicationService } from '@/services/application/rule/ruleApplicationService'
import type { RuleDTO, VoteResultDTO } from '@/repositories/rule/apiRuleRepository'

const service = new RuleApplicationService()

export function useRuleVoting() {
  // Função para buscar as regras de um projeto específico
  // Retorna uma lista de regras (RuleDTO) para o projeto

  async function fetchRules(projectId: number): Promise<RuleDTO[]> {
    const resp = await service.fetchRules(projectId, { is_open: true})
    // resp é { count, next, previous, results: RuleDTO[] }
    return (resp as any).results
  }
  async function fetchClosedRules(projectId: number): Promise<RuleDTO[]> {
    const resp = await service.fetchRules(projectId, { is_open: false })
    return (resp as any).results
  
  }
  function voteRule(
    projectId: number,
    ruleId: number,
    vote: boolean
  ): Promise<VoteResultDTO> {
    return service.voteRule(projectId, ruleId, vote)
  }
  
  function closeVoting(projectId: number, ruleId: number): Promise<any> {
    return service.closeVoting(projectId, ruleId)
  }
  return { fetchRules, fetchClosedRules, voteRule, closeVoting }
}