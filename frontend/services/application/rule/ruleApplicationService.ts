// services/application/rule/ruleApplicationService.ts
import {
  APIRuleRepository,
  RuleDTO,
  VoteResultDTO
} from '@/repositories/rule/apiRuleRepository'

export class RuleApplicationService {
  constructor(
      private readonly repository: APIRuleRepository = new APIRuleRepository()
      ) {}

  fetchRules(projectId: number): Promise<RuleDTO[]> {
    return this.repository.fetchRules(projectId)
  }

  voteRule(
    projectId: number,
    votes: { rule_id: number; vote: boolean }[]
  ): Promise<VoteResultDTO> {
    return this.repository.voteRule(projectId, votes)
  }
}