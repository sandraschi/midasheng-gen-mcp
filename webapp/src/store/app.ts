// Zustand stores: backend status, model state, LLM provider selection.
import { create } from "zustand";
import { type ModelState, api } from "../lib/api";

interface BackendState {
  ok: boolean | null;
  checking: boolean;
  refresh: () => Promise<void>;
}

export const useBackend = create<BackendState>((set) => ({
  ok: null,
  checking: false,
  refresh: async () => {
    set({ checking: true });
    try {
      const h = await api.health();
      set({ ok: h.status === "ok" });
    } catch {
      set({ ok: false });
    } finally {
      set({ checking: false });
    }
  },
}));

interface ModelStateStore {
  state: ModelState;
  device: string;
  gpuName: string | null;
  errorMessage: string | null;
  loading: boolean;
  refresh: () => Promise<void>;
  setLoading: (v: boolean) => void;
  setState: (s: ModelState) => void;
}

export const useModel = create<ModelStateStore>((set) => ({
  state: "not_installed",
  device: "auto",
  gpuName: null,
  errorMessage: null,
  loading: false,
  refresh: async () => {
    try {
      const d = await api.dashboard();
      set({
        state: d.model_state,
        device: d.device,
        gpuName: d.gpu_name,
      });
    } catch {
      /* backend unreachable - backend store handles the indicator */
    }
  },
  setLoading: (v) => set({ loading: v }),
  setState: (s) => set({ state: s }),
}));

interface LlmStore {
  providers: { name: string; port: number; detected: boolean }[];
  selectedProvider: string;
  selectedModel: string;
  models: string[];
  detected: string[];
  probing: boolean;
  refresh: () => Promise<void>;
  setProvider: (name: string) => void;
  setModel: (name: string) => void;
  setModels: (models: string[]) => void;
}

const LS_PROVIDER = "llm_provider";
const LS_MODEL = "llm_model";

export const useLlm = create<LlmStore>((set, get) => ({
  providers: [],
  selectedProvider: localStorage.getItem(LS_PROVIDER) ?? "",
  selectedModel: localStorage.getItem(LS_MODEL) ?? "",
  models: [],
  detected: [],
  probing: false,
  refresh: async () => {
    set({ probing: true });
    try {
      const data = await api.llmDiscover();
      const detected = data.detected;
      set({
        providers: data.providers,
        detected,
        selectedProvider:
          get().selectedProvider && detected.includes(get().selectedProvider)
            ? get().selectedProvider
            : (detected[0] ?? ""),
      });
      localStorage.setItem(LS_PROVIDER, get().selectedProvider);
    } catch {
      set({ providers: [], detected: [], selectedProvider: "" });
    } finally {
      set({ probing: false });
    }
  },
  setProvider: (name) => {
    set({ selectedProvider: name, models: [], selectedModel: "" });
    localStorage.setItem(LS_PROVIDER, name);
  },
  setModel: (name) => {
    set({ selectedModel: name });
    localStorage.setItem(LS_MODEL, name);
  },
  setModels: (models) => set({ models }),
}));
