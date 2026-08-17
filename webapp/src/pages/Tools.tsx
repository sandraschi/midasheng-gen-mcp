import { RefreshCw, Wrench } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { type ToolInfo, api } from "../lib/api";

export default function Tools() {
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [selected, setSelected] = useState<ToolInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await api.tools();
      setTools(data.tools);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="mx-auto max-w-5xl space-y-4 p-6" data-testid="tools-page">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">MCP Tools</h2>
        <button
          type="button"
          onClick={load}
          className="flex items-center gap-1 rounded-md border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-md border border-red-800 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="space-y-2">
          {tools.map((tool) => (
            <button
              type="button"
              key={tool.name}
              onClick={() => setSelected(tool)}
              className={`flex w-full items-start gap-2 rounded-lg border p-3 text-left transition-colors ${
                selected?.name === tool.name
                  ? "border-amber-500/60 bg-amber-500/5"
                  : "border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800"
              }`}
              data-testid={`tool-${tool.name}`}
            >
              <Wrench className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
              <div className="min-w-0">
                <div className="font-mono text-sm text-zinc-200">{tool.name}</div>
                <div className="line-clamp-2 text-xs text-zinc-500">{tool.description}</div>
                {tool.is_app && (
                  <span className="mt-1 inline-block rounded bg-purple-500/10 px-1.5 py-0.5 text-[10px] text-purple-400">
                    prefab app
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>

        <div className="lg:col-span-2">
          {selected ? (
            <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
              <h3 className="font-mono text-sm font-semibold text-amber-400">{selected.name}</h3>
              <p className="mt-2 whitespace-pre-wrap text-sm text-zinc-300">
                {selected.description}
              </p>
              <details className="mt-4">
                <summary className="cursor-pointer text-xs text-zinc-400 hover:text-zinc-200">
                  JSON Schema
                </summary>
                <pre className="mt-2 max-h-96 overflow-auto rounded-md bg-zinc-950 p-3 text-[11px] text-zinc-400">
                  {JSON.stringify(selected.schema, null, 2)}
                </pre>
              </details>
            </div>
          ) : (
            <div className="rounded-lg border border-dashed border-zinc-800 p-8 text-center text-sm text-zinc-500">
              Select a tool to see its schema and description.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
