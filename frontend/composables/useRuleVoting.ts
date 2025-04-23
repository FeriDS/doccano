// composables/useRuleVoting.ts
import type { RuleDTO, VoteResultDTO } from '@/repositories/rule/apiRuleRepository'
import { RuleApplicationService } from '@/services/application/rule/ruleApplicationService'

const service = new RuleApplicationService()

export function useRuleVoting() {
  // Busca regras com votação aberta
  async function fetchRules(projectId: number): Promise<RuleDTO[]> {
    const resp = await service.fetchRules(projectId)
    return (resp as any).results
  }

  // Busca regras com votação encerrada
  async function fetchClosedRules(projectId: number): Promise<RuleDTO[]> {
    const resp = await service.fetchClosedRules(projectId)
    return (resp as any).results
  }

  // Envia voto (sim/não) para uma regra
  function voteRule(
    projectId: number,
    ruleId: number,
    vote: boolean
  ): Promise<VoteResultDTO> {
    return service.voteRule(projectId, ruleId, vote)
  }

  return {
    fetchRules,
    fetchClosedRules,
    voteRule
  }
}
