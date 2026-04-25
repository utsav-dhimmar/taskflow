import { RoleType } from "./enums";

export interface ProjectMemberCreate {
  user_id: string;
  role: RoleType;
}

export interface ProjectMemberUpdate {
  role: RoleType;
}

export interface ProjectMemberResponse {
  id: string;
  user_id: string;
  project_id: string;
  role: RoleType;
  created_at: string;
}
