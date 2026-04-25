import { z } from "zod";

export const authSchema = {
  userCreate: z.object({
    email: z.string().email({ message: "Invalid email address" }),
    password: z
      .string()
      .min(5, { message: "Password must be at least 5 characters" })
      .max(50, { message: "Password must not exceed 50 characters" }),
    full_name: z
      .string()
      .min(2, { message: "Full name must be at least 2 characters" })
      .max(100, { message: "Full name must not exceed 100 characters" }),
  }),

  userLogin: z.object({
    email: z.string().email({ message: "Invalid email address" }),
    password: z.string().min(1, { message: "Password is required" }),
  }),
};

export type UserCreateValues = z.infer<typeof authSchema.userCreate>;
export type UserLoginValues = z.infer<typeof authSchema.userLogin>;
