import { Profile } from '../models/profile/profile'
import { BaseRepository } from './base'

export interface ProfileRepository {
  list(): Promise<Profile[]>
  create(profile: Omit<Profile, 'id'>): Promise<Profile>
  update(id: number, profile: Partial<Profile>): Promise<Profile>
  delete(id: number): Promise<void>
}

export class APIProfileRepository extends BaseRepository implements ProfileRepository {
  async list(): Promise<Profile[]> {
    const response = await this.client.get('/profiles/')
    return response.data
  }

  async create(profile: Omit<Profile, 'id'>): Promise<Profile> {
    const response = await this.client.post('/profiles/', profile)
    return response.data
  }

  async update(id: number, profile: Partial<Profile>): Promise<Profile> {
    const response = await this.client.put(`/profiles/${id}/`, profile)
    return response.data
  }

  async delete(id: number): Promise<void> {
    await this.client.delete(`/profiles/${id}/`)
  }
} 