import type { HealthResponse, RunRequest, RunResponse } from "@/types";

// Thin, credential-free API layer. The UI talks to the backend only through
// these two endpoints (GET /health and POST /run) via the dev proxy / the
// same-origin production build. All conclusions come back from the server.

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function readJson<T>(response: Response): Promise<T> {
  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError("Malformed response from the investigation service", response.status);
  }
}

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  let response: Response;
  try {
    response = await fetch("/health", { signal });
  } catch {
    throw new ApiError("Backend unreachable — is the FastAPI service running?");
  }
  if (!response.ok) {
    throw new ApiError(`Health check failed: ${response.status}`, response.status);
  }
  return readJson<HealthResponse>(response);
}

export async function runInvestigation(
  request: RunRequest,
  signal?: AbortSignal,
): Promise<RunResponse> {
  let response: Response;
  try {
    response = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sample_mode: true, ...request }),
      signal,
    });
  } catch {
    throw new ApiError("Could not reach the investigation service");
  }
  if (!response.ok) {
    throw new ApiError(
      `Investigation failed (HTTP ${response.status}). The runtime may be unavailable.`,
      response.status,
    );
  }
  return readJson<RunResponse>(response);
}
