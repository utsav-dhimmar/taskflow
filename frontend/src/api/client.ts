import axios from "axios";
const BACKEND_ENDPOINT =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export const client = axios.create({
  baseURL: BACKEND_ENDPOINT,
  headers: {
    "Content-Type": "application/json",
  },
});
