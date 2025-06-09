import { Perspective } from './perspective'

export class ProjectPerspective {
  constructor(
    public id: number,
    public project: number,
    public perspective: Perspective,
    public created_by: number,
    public created_at: string,
    public updated_at: string
  ) {}
} 