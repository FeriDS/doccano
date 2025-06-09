import { ProjectPerspective } from './projectPerspective'

export class UserPerspectiveAnswer {
  constructor(
    public id: number,
    public project_perspective: ProjectPerspective,
    public user: number,
    public field_values: { [key: string]: any },
    public is_complete: boolean,
    public created_at: string,
    public updated_at: string
  ) {}
} 