export type FieldType = 'text' | 'number' | 'boolean' | 'choice' | 'multiple'

export class PerspectiveField {
  constructor(
    public id: number,
    public name: string,
    public description: string,
    public field_type: FieldType,
    public required: boolean,
    public choices: string[] = [],
    public created_at?: string,
    public updated_at?: string
  ) {}
} 