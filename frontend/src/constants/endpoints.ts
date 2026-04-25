export const ENDPOINTS = {
  auth: {
    register: "/auth/register",
    login: "/auth/login",
    refresh: "/auth/refresh",
    logout: "/auth/logout",
    me: "/auth/me",
  },
  user: {
    me: "/users/me",
    profile: (id: string) => `/users/${id}`,
    status: (id: string) => `/users/${id}/status`,
  },
  projects: {
    list: "/projects",
    detail: (id: string) => `/projects/${id}`,
    members: (id: string) => `/projects/${id}/members`,
    member: (projectId: string, userId: string) =>
      `/projects/${projectId}/members/${userId}`,
  },
  tasks: {
    listByProject: (projectId: string) => `/projects/${projectId}/tasks`,
    detail: (id: string) => `/tasks/${id}`,
  },
} as const;
