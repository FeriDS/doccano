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
  vote: boolean | null 
}

export class APIRuleRepository {
  constructor(private readonly request = ApiService) {}

  async fetchRules(projectId: number, params?: Record<string, any>): Promise<RuleDTO[]> {
    const url = `/projects/${projectId}/rules/`
    const response = await this.request.get(url,{params})
    return response.data as RuleDTO[]
  }

  async voteRule(
    projectId: number,
    votes: { rule_id: number; vote: boolean }[]
  ): Promise<VoteResultDTO> {
    const url = `/projects/${projectId}/rules/vote/`
    const response = await this.request.post(url, { votes })
    return response.data as VoteResultDTO
  }

  closeVoting(projectId: number, ruleId: number): Promise<any> {
    const url = `/projects/${projectId}/rules/${ruleId}/`
    return this.request.patch(url, { is_open: false })
  }
}