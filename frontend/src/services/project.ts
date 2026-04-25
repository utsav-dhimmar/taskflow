import { client } from "@/api/client";
import type {
  ProjectCreateValues,
  ProjectUpdateValues,
} from "@/schemas/project";
import type { ProjectResponse, ProjectMemberResponse } from "@/types";

export const projectService = {
  /**
   * Create a new project
   */
  create: async (data: ProjectCreateValues): Promise<ProjectResponse> => {
    const res = await client.post<ProjectResponse>("/projects", data, {
      withCredentials: true,
    });
    return res.data;
  },

  /**
   * Get all projects for current user
   */
  getAll: async (): Promise<ProjectResponse[]> => {
    const res = await client.get<ProjectResponse[]>("/projects", {
      withCredentials: true,
    });
    return res.data;
  },

  /**
   * Get project by ID
   */
  getById: async (projectId: string): Promise<ProjectResponse> => {
    const res = await client.get<ProjectResponse>(`/projects/${projectId}`, {
      withCredentials: true,
    });
    return res.data;
  },

  /**
   * Update project
   */
  update: async (
    projectId: string,
    data: ProjectUpdateValues,
  ): Promise<ProjectResponse> => {
    const res = await client.patch<ProjectResponse>(
      `/projects/${projectId}`,
      data,
      {
        withCredentials: true,
      },
    );
    return res.data;
  },

  /**
   * Delete project
   */
  delete: async (projectId: string): Promise<void> => {
    await client.delete(`/projects/${projectId}`, {
      withCredentials: true,
    });
  },

  // Project Members

  /**
   * Add a member to a project
   */
  addMember: async (
    projectId: string,
    data: any,
  ): Promise<ProjectMemberResponse> => {
    const res = await client.post<ProjectMemberResponse>(
      `/projects/${projectId}/members`,
      data,
      {
        withCredentials: true,
      },
    );
    return res.data;
  },

  /**
   * Get all members of a project
   */
  getMembers: async (projectId: string): Promise<ProjectMemberResponse[]> => {
    const res = await client.get<ProjectMemberResponse[]>(
      `/projects/${projectId}/members`,
      {
        withCredentials: true,
      },
    );
    return res.data;
  },

  /**
   * Update project member role
   */
  updateMemberRole: async (
    projectId: string,
    userId: string,
    data: any,
  ): Promise<ProjectMemberResponse> => {
    const res = await client.patch<ProjectMemberResponse>(
      `/projects/${projectId}/members/${userId}`,
      data,
      {
        withCredentials: true,
      },
    );
    return res.data;
  },

  /**
   * Remove a member from a project
   */
  removeMember: async (projectId: string, userId: string): Promise<void> => {
    await client.delete(`/projects/${projectId}/members/${userId}`, {
      withCredentials: true,
    });
  },
};
