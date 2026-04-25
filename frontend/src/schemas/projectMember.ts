import { z } from "zod";

export const projectMemberSchema = {
  projectMemberCreate: z.object({
    user_id: z
      .uuid({ version: "v6", message: "Invalid user ID format" })
      .min(1, { message: "User ID is required" }),
    role: z.enum(["admin", "user"]),
  }),

  projectMemberUpdate: z.object({
    role: z.enum(["admin", "user"]),
  }),
};

export type ProjectMemberCreateValues = z.infer<
  typeof projectMemberSchema.projectMemberCreate
>;
export type ProjectMemberUpdateValues = z.infer<
  typeof projectMemberSchema.projectMemberUpdate
>;
