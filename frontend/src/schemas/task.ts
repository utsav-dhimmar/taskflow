import { z } from "zod";

import { ProjectStatus, ProjectPriority } from "@/types/enums";

export const taskSchema = {
  taskCreate: z.object({
    title: z
      .string()
      .min(1, { message: "Task title is required" })
      .max(200, { message: "Task title must not exceed 200 characters" }),
    description: z
      .string()
      .max(1000, { message: "Description must not exceed 1000 characters" })
      .optional()
      .or(z.literal("").transform(() => undefined)),
    status: z.nativeEnum(ProjectStatus).optional(),
    priority: z.nativeEnum(ProjectPriority).optional(),
    assigned_to: z
      .string()
      .uuid({ message: "Invalid user ID format" })
      .optional()
      .or(z.literal("").transform(() => undefined)),
    due_datetime: z
      .string()
      .datetime({ message: "Invalid date format" })
      .optional()
      .or(z.literal("").transform(() => undefined)),
  }),

  taskUpdate: z.object({
    title: z
      .string()
      .min(1, { message: "Task title is required" })
      .max(200, { message: "Task title must not exceed 200 characters" })
      .optional(),
    description: z
      .string()
      .max(1000, { message: "Description must not exceed 1000 characters" })
      .optional()
      .or(z.literal("").transform(() => undefined)),
    status: z.nativeEnum(ProjectStatus).optional(),
    priority: z.nativeEnum(ProjectPriority).optional(),
    assigned_to: z
      .string()
      .uuid({ message: "Invalid user ID format" })
      .optional()
      .or(z.literal("").transform(() => undefined)),
    due_datetime: z
      .string()
      .datetime({ message: "Invalid date format" })
      .optional()
      .or(z.literal("").transform(() => undefined)),
  }),
};

export type TaskCreateValues = z.infer<typeof taskSchema.taskCreate>;
export type TaskUpdateValues = z.infer<typeof taskSchema.taskUpdate>;
