import { Download, RefreshCw, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/api";
import { useLlm, useModel } from "../store/app";

export default function Settings() {
  const modelState = useModel((s) => s.state);
  const modelDevice = useModel((s) => s.device);
  const modelGpu = useModel((s) => s.gpuName);
  const modelError = useModel((s) => s.errorMessage);
  const modelRefresh = useModel((s) => s.refresh);
  const llmRefresh = useLlm((s) => s.refresh);
  const llmProviders = useLlm((s) => s.providers);
  const llmSelectedProvider = useLlm((s) => s.selectedProvider);
  const llmSelectedModel = useLlm((s) => s.selectedModel);
  const llmModels = useLlm((s) => s.models);
  const llmProbing = useLlm((s) => s.probing);
  const llmDetected = useLlm((s) => s.detected);
  const llmSetProvider = useLlm((s) => s.setProvider);
  const llmSetModel = useLlm((s) => s.setModel);
  const llmSetModels = useLlm((s) => s.setModels);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refreshAll = useCallback(() => {
    void modelRefresh();
    void llmRefresh();
  }, [modelRefresh, llmRefresh]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  const modelAction = async (action: "download" | "load" | "unload") => {
    setBusy(action);
    setError(null);
    try {
      const resp = await fetch(`/api/model/${action}`, { method: "POST" });
      if (!resp.ok) {
        const body = await resp.json().catch(() => null);
        throw new Error(body?.detail ?? `Model ${action} failed`);
      }
      await modelRefresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : `${action} failed`);
    } finally {
      setBusy(null);
    }
  };

  // Fetch Ollama models when a provider is selected
  useEffect(() => {
    if (!llmSelectedProvider || llmSelectedProvider !== "ollama") return;
    fetch("http://127.0.0.1:11434/api/tags")
      .then((r) => r.json())
      .then((d) => {
        const names = (d.models ?? []).map((m: { name: string }) => m.name);
        llmSetModels(names);
        if (names.length > 0 && !names.includes(llmSelectedModel)) {
          llmSetModel(names[0]);
        }
      })
      .catch(() => llmSetModels([]));
  }, [llmSelectedProvider, llmSelectedModel, llmSetModel, llmSetModels]);

  const resetLibrary = async () => {
    if (
      !window.confirm(
        "Delete ALL scenes from the library? This permanently removes every WAV file.",
      )
    )
      return;
    try {
      let offset = 0;
      for (;;) {
        const page = await api.scenes(100, offset);
        for (const scene of page.items) {
          await api.deleteScene(scene.id);
        }
        if (!page.has_more) break;
        offset += 100;
      }
      await modelRefresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Reset failed");
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6" data-testid="settings-page">
      <h2 className="text-lg font-semibold">Settings</h2>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
        <h3 className="mb-3 text-sm font-medium text-zinc-300">Model & Backend</h3>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="text-zinc-500">State</div>
          <div className="font-mono text-zinc-200" data-testid="model-state">
            {modelState}
          </div>
          <div className="text-zinc-500">Model ID</div>
          <div className="font-mono text-zinc-200">mispeech/midashenglm-gen</div>
          <div className="text-zinc-500">Device</div>
          <div className="text-zinc-200">{modelDevice}</div>
          <div className="text-zinc-500">GPU</div>
          <div className="text-zinc-200">{modelGpu ?? "none (CPU)"}</div>
        </div>
        {modelError && (
          <div className="mt-3 rounded-md border border-red-800 bg-red-950/40 p-2 text-xs text-red-300">
            {modelError}
          </div>
        )}
        {error && (
          <div className="mt-3 rounded-md border border-red-800 bg-red-950/40 p-2 text-xs text-red-300">
            {error}
          </div>
        )}
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => modelAction("download")}
            disabled={busy !== null}
            data-testid="model-download"
            className="flex items-center gap-1 rounded-md bg-amber-500 px-3 py-1.5 text-xs font-medium text-zinc-950 hover:bg-amber-400 disabled:opacity-50"
          >
            <Download className="h-3.5 w-3.5" />
            {busy === "download" ? "Downloading..." : "Download Model"}
          </button>
          <button
            type="button"
            onClick={() => modelAction("load")}
            disabled={busy !== null}
            data-testid="model-load"
            className="rounded-md border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800 disabled:opacity-50"
          >
            {busy === "load" ? "Loading..." : "Load into GPU"}
          </button>
          <button
            type="button"
            onClick={() => modelAction("unload")}
            disabled={busy !== null}
            data-testid="model-unload"
            className="rounded-md border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800 disabled:opacity-50"
          >
            Unload
          </button>
          <button
            type="button"
            onClick={refreshAll}
            className="flex items-center gap-1 rounded-md border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </button>
        </div>
      </section>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
        <h3 className="mb-3 text-sm font-medium text-zinc-300">Local LLM (Chat page)</h3>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="text-zinc-500">Provider</div>
          <div>
            <select
              value={llmSelectedProvider}
              onChange={(e) => llmSetProvider(e.target.value)}
              data-testid="llm-provider-select"
              className="rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1 text-xs text-zinc-200 focus:border-amber-500 focus:outline-none"
            >
              {llmProviders.length === 0 && <option value="">No local LLM detected</option>}
              {llmProviders.map((p) => (
                <option key={p.name} value={p.name}>
                  {p.name} :{p.port}
                </option>
              ))}
            </select>
          </div>
          <div className="text-zinc-500">Model</div>
          <div>
            <select
              value={llmSelectedModel}
              onChange={(e) => llmSetModel(e.target.value)}
              data-testid="llm-model-select"
              className="rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1 text-xs text-zinc-200 focus:border-amber-500 focus:outline-none"
            >
              {llmModels.length === 0 && <option value="">No models found</option>}
              {llmModels.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-3 text-xs">
          {llmProbing ? (
            <span className="text-zinc-500">Probing local providers...</span>
          ) : llmDetected.length > 0 ? (
            <span className="text-green-400">Detected: {llmDetected.join(", ")}</span>
          ) : (
            <span className="text-zinc-500">
              No local LLM detected. Install Ollama or LM Studio to enable AI features in the Chat
              page.
            </span>
          )}
        </div>
      </section>

      <section className="rounded-lg border border-red-900/40 bg-zinc-900/60 p-4">
        <h3 className="mb-2 text-sm font-medium text-red-300">Danger Zone</h3>
        <button
          type="button"
          onClick={resetLibrary}
          data-testid="library-reset"
          className="flex items-center gap-1 rounded-md border border-red-800 px-3 py-1.5 text-xs text-red-300 hover:bg-red-950/40"
        >
          <Trash2 className="h-3.5 w-3.5" /> Delete all scenes
        </button>
      </section>
    </div>
  );
}
