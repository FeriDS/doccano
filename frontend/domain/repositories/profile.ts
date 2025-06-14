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
    console.log('Fetching profiles...')
    const response = await this.client.get('/profiles/')
    console.log('Profiles response:', response.data)
    return response.data
  }

  async create(profile: Omit<Profile, 'id'>): Promise<Profile> {
    console.log('Creating profile:', profile)
    const response = await this.client.post('/profiles/', profile)
    console.log('Create response:', response.data)
    return response.data
  }

  async update(id: number, profile: Partial<Profile>): Promise<Profile> {
    console.log('Updating profile:', { id, profile })
    const response = await this.client.put(`/profiles/${id}/`, profile)
    console.log('Update response:', response.data)
    return response.data
  }

  async delete(id: number): Promise<void> {
    console.log('Deleting profile:', id)
    await this.client.delete(`/profiles/${id}/`)
  }
} 