import { createFileRoute } from "@tanstack/react-router";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useForm } from "react-hook-form";
import type z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginAuthLoginPostBody } from "@/api/schema";
import { Button } from "@/components/ui/button";
import { loginAuthLoginPost, readUsersMeAuthMeGet } from "@/api/auth/auth";
export const Route = createFileRoute("/auth/login")({
  component: RouteComponent,
});

function RouteComponent() {
  const form = useForm<z.infer<typeof loginAuthLoginPostBody>>({
    resolver: zodResolver(loginAuthLoginPostBody),
    defaultValues: {
      email: "",
      password: "",
    },
  });
  async function onSubmit(values: z.infer<typeof loginAuthLoginPostBody>) {
    // Do something with the form values.
    // ✅ This will be type-safe and validated.
    // console.log(values);
    const res = await loginAuthLoginPost(values);
    console.table(res);
    console.log(res.data);
  }
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input placeholder="Email" {...field} />
              </FormControl>
              <FormDescription>Enter Mail</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input placeholder="Password" {...field} />
              </FormControl>
              {/* <FormDescription>
                This is your public display name.
              </FormDescription> */}
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
      <Button
        onClick={async (e) => {
          const data = await readUsersMeAuthMeGet({
            withCredentials: true,
          });
          console.log(data);
        }}
      >
        Get info
      </Button>
    </Form>
  );
}
