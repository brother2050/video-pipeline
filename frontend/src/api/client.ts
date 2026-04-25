import axios, { AxiosError } from "axios";
import type { APIResponse } from "@/types";

export class APIError extends Error {
  statusCode: number;
  apiMessage: string | null;

  constructor(statusCode: number, message: string, apiMessage: string | null) {
    super(message);
    this.name = "APIError";
    this.statusCode = statusCode;
    this.apiMessage = apiMessage;
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "NetworkError";
  }
}

const client = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  timeout: 60_000,
});

client.interceptors.response.use(
  (response) => {
    const data = response.data as APIResponse<unknown>;
    if (data && typeof data === "object" && "success" in data) {
      if (!data.success) {
        throw new APIError(
          response.status,
          data.message || "Request failed",
          data.message
        );
      }
      // 解包 data 字段
      response.data = data.data;
    }
    return response;
  },
  (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status;
      const responseData = error.response.data as Record<string, unknown> | undefined;
      const message =
        (responseData?.message as string) || error.message;
      throw new APIError(status, message, message);
    }
    if (error.code === "ECONNABORTED" || error.message.includes("timeout")) {
      throw new NetworkError("Request timed out");
    }
    throw new NetworkError("Network error: " + error.message);
  }
);

export default client;
