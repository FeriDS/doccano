export class UserItem {
  constructor(
    readonly id: number,
    readonly username: string,
    readonly email: string,
    readonly first_name: string,
    readonly last_name: string,
    readonly isSuperuser: boolean,
    readonly isStaff: boolean,
    readonly isGlobalAdmin: boolean,
    readonly created_by: number | null = null
  ) {}
}
