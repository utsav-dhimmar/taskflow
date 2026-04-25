export type RoleType = "admin" | "user";

export interface UserBase {
  id: string;
  email: string;
  full_name: string;
  role: RoleType;
  is_active: boolean;
}

export interface UserUpdate {
  full_name?: string | null;
}

export interface UserStatusUpdate {
  is_active: boolean;
}

export interface UserResponse extends UserBase {}
