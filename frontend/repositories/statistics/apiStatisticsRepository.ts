import ApiService from '@/services/api.service'

export interface AnnotationStatistics {
  statistics: {
    disagreementRate: number
    perspectiveCount: number
    resolutionRate: number
  }
  disagreements: Array<{
    id: number
    textId: string
    category: string
    type: string
    annotators: string[]
    status: string
    text: string
    annotations: Array<{
      id: number
      annotator: string
      label: string
      perspective: string
    }>
    discussion: Array<{
      id: number
      user: string
      text: string
      timestamp: string
    }>
  }>
  disagreementByCategory: Array<{
    category: string
    count: number
  }>
  perspectiveDistribution: Array<{
    perspective: string
    count: number
  }>
}

export class APIStatisticsRepository {
  constructor(private readonly request = ApiService) {}

  async fetchAnnotationStatistics(projectId: string, params: any): Promise<AnnotationStatistics> {
    const url = `/projects/${projectId}/statistics/annotations`
    const response = await this.request.get(url, { params })
    return response.data
  }
} 