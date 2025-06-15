// repositories/rule/apiRuleRepository.ts
import ApiService from '@/services/api.service'

export interface RuleDTO {
  id: number
  rule: { id: number; text: string }
  votes_yes: number
  votes_no: number
  user_has_voted: boolean
  is_open: boolean
}

export interface VoteResultDTO {
  votes_yes: number
  votes_no: number
  user_has_voted: boolean
  is_open: boolean
}

export class APIRuleRepository {
  constructor(private readonly request = ApiService) {}

  async fetchRules(projectId: number): Promise<RuleDTO[]> {
    const url = `/projects/${projectId}/rules/`
    const response = await this.request.get(url)
    return response.data as RuleDTO[]
  }

  async voteRule(
    projectId: number,
    ruleId: number,
    vote: boolean
  ): Promise<VoteResultDTO> {
    const url = `/projects/${projectId}/rules/${ruleId}/vote/`
    const response = await this.request.post(url, { vote })
    return response.data as VoteResultDTO
  }
}