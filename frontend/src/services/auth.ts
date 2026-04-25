import { client } from "@/api/client";
import type { UserCreateValues, UserLoginValues } from "@/schemas/auth";
import type { UserResponse } from "@/types/auth";

export const authService = {
	/**
	 * Register a new user
	 */
	register: async (data: UserCreateValues): Promise<UserResponse> => {
		const res = await client.post<UserResponse>("/auth/register", data);
		return res.data;
	},

	/**
	 * Login a user
	 */
	login: async (data: UserLoginValues): Promise<UserResponse> => {
		const res = await client.post<UserResponse>("/auth/login", data, {
			withCredentials: true,
		});
		return res.data;
	},

	/**
	 * Refresh access token
	 */
	refresh: async (): Promise<UserResponse> => {
		const res = await client.post<UserResponse>(
			"/auth/refresh",
			{},
			{
				withCredentials: true,
			},
		);
		return res.data;
	},

	/**
	 * Logout the current user
	 */
	logout: async (): Promise<void> => {
		await client.post("/auth/logout", {}, { withCredentials: true });
	},

	/**
	 * Get current user profile
	 */
	getMe: async (): Promise<UserResponse> => {
		const res = await client.get<UserResponse>("/auth/me", {
			withCredentials: true,
		});
		return res.data;
	},
};
