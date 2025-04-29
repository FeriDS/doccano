import type { RuleDTO, VoteResultDTO } from '@/repositories/rule/apiRuleRepository'
import { RuleApplicationService } from '@/services/application/rule/ruleApplicationService'

const service = new RuleApplicationService()

export function useRuleVoting() {
  async function fetchRules(projectId: number): Promise<RuleDTO[]> {
    const resp = await service.fetchRules(projectId, { is_open: true })
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

  function createRule(projectId: number, data: { text: string }): Promise<RuleDTO> {
    return service.createRule(projectId, data)
  }

  return {
    fetchRules,
    fetchClosedRules,
    voteRule,
    closeVoting,
    createRule
  }
}
