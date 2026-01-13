import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/me/$name")({
  component: RouteComponent,
  // loader:async({params})=>{

  // }
});

function RouteComponent() {
  const { name } = Route.useParams();
  return <div>Hello {name}</div>;
}
