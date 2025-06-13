import { UserItem } from '@/domain/models/user/user'
import { UserRepository } from '@/domain/repositories/index'
import ApiService from '@/services/api.service'

function toModel(item: { [key: string]: any }): UserItem {
  return new UserItem(
    item.id,
    item.username,
    item.email,
    item.is_staff,
    item.is_superuser,
    item.profiles || []
  )
}

export class APIUserRepository implements UserRepository {
  constructor(private readonly request = ApiService) {}

  async getProfile(): Promise<UserItem> {
    const url = '/me'
    const response = await this.request.get(url)
    return toModel(response.data)
  }

  async list(query: string): Promise<UserItem[]> {
    const url = `/users?q=${query}`
    const response = await this.request.get(url)
    return response.data.map((item: { [key: string]: any }) => toModel(item))
  }

  async createUser(user: {
    username: string
    email: string
    password: string
    profiles: number[]
  }): Promise<UserItem> {
    const url = '/users/'
    const response = await this.request.post(url, user)
    return toModel(response.data)
  }

  async updateUser(id: number, user: Partial<UserItem>): Promise<UserItem> {
    const url = `/users/${id}/`
    const response = await this.request.put(url, user)
    return toModel(response.data)
  }

  async deleteUser(id: number): Promise<void> {
    const url = `/users/${id}/`
    await this.request.delete(url)
  }

  async getIdByUsername(username: string): Promise<number> {
    const users = await this.list(username)
    const foundUser = users.find(user => user.username === username)
    if (!foundUser) {
      throw new Error(`User with username ${username} not found.`)
    }
    return foundUser.id
  }
}
