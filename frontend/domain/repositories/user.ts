import { BaseRepository } from './base'
import { UserItem } from '../models/user/user'
import { UserRepository } from './index'

export class APIUserRepository extends BaseRepository implements UserRepository {
  async list(query: string): Promise<UserItem[]> {
    const response = await this.client.get(`/users/?q=${query}`)
    return response.data
  }

  async createUser(user: {
    username: string
    email: string
    password: string
    profiles: number[]
  }): Promise<UserItem> {
    const response = await this.client.post('/users/', user)
    return response.data
  }

  async updateUser(id: number, user: Partial<UserItem>): Promise<UserItem> {
    const response = await this.client.put(`/users/${id}/`, user)
    return response.data
  }

  async deleteUser(id: number): Promise<void> {
    await this.client.delete(`/users/${id}/`)
  }

  async getProfile(): Promise<UserItem> {
    const response = await this.client.get('/users/me/')
    return response.data
  }
} 