import { zodResolver } from "@hookform/resolvers/zod";
import { createFileRoute } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import z, { email } from "zod";

import { Button } from "@/components/ui/button";
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
export const Route = createFileRoute("/auth/login")({
  component: RouteComponent,
});

const loginBody = z.object({
  email: z.email(),
  password: z.string().min(8),
});
type LoginBody = z.infer<typeof loginBody>;
function RouteComponent() {
  const form = useForm<LoginBody>({
    resolver: zodResolver(loginBody),
  });
  async function onSubmit(values: LoginBody) {
    console.log(values);
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
