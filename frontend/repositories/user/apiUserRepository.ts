import { UserItem } from '@/domain/models/user/user'
import ApiService from '@/services/api.service'

function toModel(item: { [key: string]: any }): UserItem {
  return new UserItem(
    item.id,
    item.username,
    item.email,
    item.first_name || '',
    item.last_name || '',
    item.is_superuser,
    item.is_staff,
    item.is_global_admin || false,
    item.created_by
  )
}

export class APIUserRepository {
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

  async deleteUser(userId: number): Promise<void> {
    const url = `/users/delete/${userId}`;
    await this.request.delete(url);
  }
  
  async updateUser(
    userId: number,
    data: {
      username?: string
      first_name?: string
      last_name?: string
      email?: string
      isStaff?: boolean
      isSuperuser?: boolean
    }
  ): Promise<UserItem> {
    const url = `/users/update/${userId}`;
    console.log('Sending update data:', data);
    const response = await this.request.patch(url, {
      username: data.username,
      first_name: data.first_name,
      last_name: data.last_name,
      email: data.email,
      is_staff: data.isStaff,
      is_superuser: data.isSuperuser
    });
    console.log('Update response:', response.data);
    return toModel(response.data);
  }

  async getIdByUsername(username: string): Promise<number> {
    // Reuse the list method to fetch users matching the query.
    const users = await this.list(username);
    // Find the user with the exact username.
    const foundUser = users.find(user => user.username === username);
    if (!foundUser) {
      throw new Error(`User with username ${username} not found.`);
    }
    return foundUser.id;
  }
}
