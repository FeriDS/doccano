import { APIUserRepository } from './user'
import { APIProfileRepository } from './profile'
import { UserItem } from '../models/user/user'
import { Profile } from '../models/profile/profile'

export interface UserRepository {
  list: (query: string) => Promise<UserItem[]>
  createUser: (user: {
    username: string
    email: string
    password: string
    profiles: number[]
  }) => Promise<UserItem>
  updateUser: (id: number, user: Partial<UserItem>) => Promise<UserItem>
  deleteUser: (id: number) => Promise<void>
  getProfile: () => Promise<UserItem>
}

export interface ProfileRepository {
  list: () => Promise<Profile[]>
  create: (profile: Partial<Profile>) => Promise<Profile>
  update: (id: number, profile: Partial<Profile>) => Promise<Profile>
  delete: (id: number) => Promise<void>
}

export type { UserItem, Profile }
export { APIUserRepository, APIProfileRepository } 