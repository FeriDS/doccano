export interface Rule {
  id: number
  title: string
  description: string
  created_at: string
  updated_at: string
  created_by: number
}

export interface ProjectRule {
  id: number
  project: number
  rule: Rule
  is_required: boolean
  created_at: string
  updated_at: string
  vote_count: {
    agree: number
    disagree: number
    neutral: number
    total: number
  }
}

export interface RuleVote {
  id: number
  project_rule: number
  user: number
  vote: 'agree' | 'disagree' | 'neutral'
  comment?: string
  created_at: string
  updated_at: string
} 