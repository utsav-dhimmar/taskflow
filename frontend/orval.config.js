import { defineConfig } from "orval";

export default defineConfig({
  petstore: {
    output: {
      client: "zod",
      mode: "single",
      target: "./src/api/schema.ts",
    },
    input: {
      target: `http://127.0.0.1:8000/api/openapi.json`,
    },
    hooks: {
      afterAllFilesWrite: "prettier --write",
    },
  },
  petstoreAxios: {
    input: {
      target: `http://127.0.0.1:8000/api/openapi.json`,
    },
    output: {
      mode: "tags-split",
      client: "axios-functions",
      target: "src/api/client.ts",
      httpClient: "axios",
      baseUrl: "http://127.0.0.1:8000/",
      prettier: true,
      // fileExtension: ".zod.ts",
    },
  },
});
