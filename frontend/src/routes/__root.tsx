import { Outlet, createRootRoute } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import * as React from "react";

import { Button } from "@/components/ui/button";
export const Route = createRootRoute({
  component: RootComponent,
  notFoundComponent: () => <div>Not Found</div>,
  preload: true,
});

function RootComponent() {
  return (
    <React.Fragment>
      <div>Hello "__root"!</div>
      <Button
        onClick={(k) => {
          console.log("Hi", k.type);
        }}
      >
        Click Me
      </Button>
      <Outlet />
      <TanStackRouterDevtools />
    </React.Fragment>
  );
}
