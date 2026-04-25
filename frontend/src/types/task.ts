import { ProjectStatus, ProjectPriority } from "./enums";

export interface TaskCreate {
  title: string;
  description?: string | null;
  status?: ProjectStatus;
  priority?: ProjectPriority;
  assigned_to?: string | null;
  due_datetime?: string | null;
}

export interface TaskUpdate {
  title?: string | null;
  description?: string | null;
  status?: ProjectStatus | null;
  priority?: ProjectPriority | null;
  assigned_to?: string | null;
  due_datetime?: string | null;
}

export interface TaskResponse {
  id: string;
  project_id: string;
  title: string;
  description?: string | null;
  status: ProjectStatus;
  priority: ProjectPriority;
  assigned_to?: string | null;
  created_by: string;
  due_datetime?: string | null;
  created_at: string;
  updated_at: string;
}
