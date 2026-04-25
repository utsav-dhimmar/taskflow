import { z } from "zod";

export const projectSchema = {
  projectCreate: z.object({
    name: z
      .string()
      .min(1, { message: "Project name is required" })
      .max(100, { message: "Project name must not exceed 100 characters" }),
    description: z
      .string()
      .max(500, { message: "Description must not exceed 500 characters" })
      .optional()
      .or(z.literal("").transform(() => undefined)),
  }),

  projectUpdate: z.object({
    name: z
      .string()
      .min(1, { message: "Project name is required" })
      .max(100, { message: "Project name must not exceed 100 characters" })
      .optional(),
    description: z
      .string()
      .max(500, { message: "Description must not exceed 500 characters" })
      .optional()
      .or(z.literal("").transform(() => undefined)),
  }),
};

export type ProjectCreateValues = z.infer<typeof projectSchema.projectCreate>;
export type ProjectUpdateValues = z.infer<typeof projectSchema.projectUpdate>;
