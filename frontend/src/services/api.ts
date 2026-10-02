import axios from "axios";
import { QueryResponse, StreamEvent } from "../types";

const API_BASE = "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function healthCheck(): Promise<any> {
  const response = await apiClient.get("/health");
  return response.data;
}

export async function queryStream(
  query: string,
  top_k: number = 8,
  onEvent: (event: StreamEvent) => void
): Promise<void> {
  const eventSource = new EventSource(
    `/api/v1/query/stream?query=${encodeURIComponent(query)}&top_k=${top_k}`
  );

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onEvent(data);

      if (data.type === "complete" || data.type === "error") {
        eventSource.close();
      }
    } catch (err) {
      console.error("Failed to parse event:", err);
    }
  };

  eventSource.onerror = () => {
    eventSource.close();
    onEvent({
      type: "error",
      error_message: "Connection lost",
    });
  };
}
