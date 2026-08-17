// Local LLM provider detection (WEBAPP_SOTA section VI).
import { type LlmProvider, api } from "./api";

export const PROVIDER_PORTS: Record<string, number> = {
  ollama: 11434,
  lmstudio: 1234,
  vllm: 8000,
};

export async function detectProviders(): Promise<LlmProvider[]> {
  try {
    const data = await api.llmDiscover();
    return data.providers;
  } catch {
    return [];
  }
}
