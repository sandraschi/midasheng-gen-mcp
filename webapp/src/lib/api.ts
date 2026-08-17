// Backend API client. All calls go through the Vite proxy in dev
// (same-origin /api), which forwards to the backend on 11159.
export const API_BASE = "";

export type ModelState =
  | "not_installed"
  | "model_missing"
  | "unloaded"
  | "loading"
  | "ready"
  | "error";

export interface Health {
  status: string;
  server: string;
  version: string;
  uptime_seconds: number;
  tool_count: number;
  providers: {
    model: {
      state: string;
      device: string;
      gpu_name: string | null;
      cuda_available: boolean;
    };
  };
}

export interface Scene {
  id: string;
  created_at: string;
  caption: Record<string, string | null>;
  params: Record<string, unknown>;
  duration_seconds: number | null;
  sample_rate: number | null;
  size_bytes: number | null;
  status: string;
  job_id: string | null;
  audio_url: string;
}

export interface ScenePage {
  items: Scene[];
  total: number;
  has_more: boolean;
  limit: number;
  offset: number;
}

export interface Job {
  id: string;
  status: string;
  progress: number;
  message: string;
  scene_id: string | null;
  created_at: string;
  finished_at: string | null;
  error: string | null;
  running?: boolean;
}

export interface DashboardData {
  scene_count: number;
  total_seconds: number;
  model_state: ModelState;
  model_id: string;
  device: string;
  gpu_name: string | null;
  cuda_available: boolean;
  torch_installed: boolean;
  transformers_installed: boolean;
  version: string;
  recent: Scene[];
}

export interface ToolInfo {
  name: string;
  description: string;
  schema: Record<string, unknown>;
  is_app: boolean;
}

export interface SkillInfo {
  name: string;
  uri: string;
  description: string;
}

export interface Sample {
  id: string;
  caption: string;
  asr?: string;
  speech?: string;
  sfx?: string;
  music?: string;
  env?: string;
}

export interface LlmProvider {
  name: string;
  port: number;
  base: string;
  detected: boolean;
}

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, init);
  if (!resp.ok) {
    let detail = `HTTP ${resp.status}`;
    try {
      const body = await resp.json();
      detail = body.detail ?? detail;
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail);
  }
  return resp.json() as Promise<T>;
}

export const api = {
  health: () => http<Health>("/api/health"),
  dashboard: () => http<DashboardData>("/api/dashboard"),
  capabilities: () =>
    http<{ capabilities: { id: string; name: string; available: boolean }[] }>("/api/capabilities"),
  tools: () => http<{ tools: ToolInfo[]; count: number }>("/api/tools"),
  skills: () => http<{ skills: SkillInfo[]; count: number }>("/api/skills"),
  skill: (name: string) => http<{ name: string; content: string }>(`/api/skills/${name}`),
  samples: () => http<{ samples: Sample[]; count: number }>("/api/samples"),
  scenes: (limit = 20, offset = 0) =>
    http<ScenePage>(`/api/scenes?limit=${limit}&offset=${offset}`),
  scene: (id: string) => http<Scene>(`/api/scenes/${id}`),
  deleteScene: (id: string) =>
    http<{ success: boolean }>(`/api/scenes/${id}`, { method: "DELETE" }),
  generate: (payload: Record<string, unknown>) =>
    http<{ job_id: string; status: string }>("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  job: (id: string) => http<{ success: boolean; job: Job }>(`/api/jobs/${id}`),
  jobs: (limit = 20) => http<{ items: Job[]; total: number }>(`/api/jobs?limit=${limit}`),
  logs: (search?: string, level?: string, limit = 200) =>
    http<{ entries: { ts: string; level: string; source: string; message: string }[] }>(
      `/api/logs?limit=${limit}${level ? `&level=${level}` : ""}${
        search ? `&search=${encodeURIComponent(search)}` : ""
      }`,
    ),
  llmDiscover: () =>
    http<{ providers: LlmProvider[]; detected: string[]; default_model: string }>(
      "/api/llm/discover",
    ),
  llmChat: (messages: { role: string; content: string }[], model?: string) =>
    http<{ success: boolean; content: string; model: string; provider: string }>("/api/llm/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages, model }),
    }),
  modelStatus: () =>
    http<{
      state: ModelState;
      error_message: string | null;
      model_id: string;
      device: string;
      cuda_available: boolean;
      gpu_name: string | null;
    }>("/api/dashboard"),
};
