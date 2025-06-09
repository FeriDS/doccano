import { PerspectiveField } from './perspectiveField'

export class Perspective {
  constructor(
    public id: number,
    public name: string,
    public description: string,
    public fields: PerspectiveField[],
    public created_by?: number,
    public created_by_username?: string,
    public created_at?: string,
    public updated_at?: string
  ) {}
} 