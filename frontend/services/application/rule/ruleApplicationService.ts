import {
  APIRuleRepository,
  RuleDTO,
  VoteResultDTO
} from '@/repositories/rule/apiRuleRepository'

export class RuleApplicationService {
  constructor(
    private readonly repository: APIRuleRepository = new APIRuleRepository()
  ) {}

  fetchRules(projectId: number, params?: Record<string, any>): Promise<RuleDTO[]> {
    return this.repository.fetchRules(projectId, params)
  }

  fetchClosedRules(projectId: number): Promise<RuleDTO[]> {
    return this.repository.fetchRules(projectId, { is_open: false })
  }

  voteRule(
    projectId: number,
    ruleId: number,
    vote: boolean
  ): Promise<VoteResultDTO> {
    return this.repository.voteRule(projectId, ruleId, vote)
  }

  closeVoting(projectId: number, ruleId: number): Promise<any> {
    return this.repository.closeVoting(projectId, ruleId)
  }

  createRule(projectId: number, data: { text: string }): Promise<RuleDTO> {
    return this.repository.createRule(projectId, data)
  }
}
