import { ExampleItem, ExampleItemList, Assignment } from '~/domain/models/example/example'

export class ExampleDTO {
  id: number
  text: string
  meta: object
  annotationApprover: boolean | null
  commentCount: number
  isApproved: boolean
  fileUrl: string
  filename: string
  url: string
  isConfirmed: boolean
  assignments: Assignment[]
  label_distribution: { [label: string]: number }
  has_discrepancy: boolean
  annotation_start_date: string | null
  annotation_end_date: string | null
  is_finished: boolean

  constructor(item: ExampleItem) {
    this.id = item.id
    this.text = item.text
    this.meta = item.meta
    this.annotationApprover = item.annotationApprover
    this.commentCount = item.commentCount
    this.isApproved = !!item.annotationApprover
    this.fileUrl = item.fileUrl
    this.filename = item.filename
    this.url = item.url
    this.isConfirmed = item.isConfirmed
    this.assignments = item.assignments
    this.label_distribution = item.label_distribution
    this.has_discrepancy = item.has_discrepancy
    this.annotation_start_date = item.annotation_start_date
    this.annotation_end_date = item.annotation_end_date
    this.is_finished = item.is_finished
  }
}

export class ExampleListDTO {
  count: number
  next: string | null
  prev: string | null
  items: ExampleDTO[]

  constructor(item: ExampleItemList) {
    this.count = item.count
    this.next = item.next
    this.prev = item.prev
    this.items = item.items.map((_) => new ExampleDTO(_))
  }
}
