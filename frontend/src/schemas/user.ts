import { z } from "zod";

export const userSchema = {
  userUpdate: z.object({
    full_name: z
      .string()
      .min(2, { message: "Full name must be at least 2 characters" })
      .max(100, { message: "Full name must not exceed 100 characters" })
      .optional()
      .or(z.literal("").transform(() => undefined)),
  }),

  userStatusUpdate: z.object({
    is_active: z.boolean(),
  }),
};

export type UserUpdateValues = z.infer<typeof userSchema.userUpdate>;
export type UserStatusUpdateValues = z.infer<
  typeof userSchema.userStatusUpdate
>;
