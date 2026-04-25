import { RoleType } from "./enums";

export interface TokenData {
  id?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  refresh_token: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  role: RoleType;
  is_active: boolean;
}
