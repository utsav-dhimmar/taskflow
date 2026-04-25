import { client } from "@/api/client";
import type { TaskCreateValues, TaskUpdateValues } from "@/schemas/task";
import type { TaskResponse } from "@/types/task";

export const taskService = {
  /**
   * Create a new task in a project
   */
  create: async (
    projectId: string,
    data: TaskCreateValues,
  ): Promise<TaskResponse> => {
    const res = await client.post<TaskResponse>(
      `/projects/${projectId}/tasks`,
      data,
      {
        withCredentials: true,
      },
    );
    return res.data;
  },

  /**
   * Get all tasks for a project
   */
  getByProject: async (
    projectId: string,
    params?: {
      status?: string;
      priority?: string;
      page?: number;
      limit?: number;
    },
  ): Promise<TaskResponse[]> => {
    const res = await client.get<TaskResponse[]>(
      `/projects/${projectId}/tasks`,
      {
        params,
        withCredentials: true,
      },
    );
    return res.data;
  },

  /**
   * Get task by ID
   */
  getById: async (taskId: string): Promise<TaskResponse> => {
    const res = await client.get<TaskResponse>(`/tasks/${taskId}`, {
      withCredentials: true,
    });
    return res.data;
  },

  /**
   * Update task
   */
  update: async (
    taskId: string,
    data: TaskUpdateValues,
  ): Promise<TaskResponse> => {
    const res = await client.patch<TaskResponse>(`/tasks/${taskId}`, data, {
      withCredentials: true,
    });
    return res.data;
  },

  /**
   * Delete task
   */
  delete: async (taskId: string): Promise<void> => {
    await client.delete(`/tasks/${taskId}`, {
      withCredentials: true,
    });
  },
};
