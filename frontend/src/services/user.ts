import { client } from "@/api/client";
import type { UserUpdateValues, UserStatusUpdateValues } from "@/schemas/user";
import type { UserResponse } from "@/types/user";

export const userService = {
  /**
   * Get current user profile
   */
  getMe: async (): Promise<UserResponse> => {
    const res = await client.get<UserResponse>("/users/me", {
      withCredentials: true,
    });
    return res.data;
  },

  /**
   * Update current user
   */
  updateMe: async (data: UserUpdateValues): Promise<UserResponse> => {
    const res = await client.patch<UserResponse>("/users/me", data, {
      withCredentials: true,
    });
    return res.data;
  },

  /**
   * Get user by ID (admin only)
   */
  getById: async (userId: string): Promise<UserResponse> => {
    const res = await client.get<UserResponse>(`/users/${userId}`, {
      withCredentials: true,
    });
    return res.data;
  },

  /**
   * Update user status (admin only)
   */
  updateStatus: async (
    userId: string,
    data: UserStatusUpdateValues,
  ): Promise<UserResponse> => {
    const res = await client.patch<UserResponse>(
      `/users/${userId}/status`,
      data,
      {
        withCredentials: true,
      },
    );
    return res.data;
  },
};
