import { Profile } from '../profile/profile'

export class UserItem {
  constructor(
    readonly id: number,
    readonly username: string,
    readonly email: string,
    readonly isStaff: boolean,
    readonly isSuperuser: boolean,
    readonly profiles: Profile[]
  ) {}
}
