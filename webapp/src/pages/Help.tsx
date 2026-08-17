export default function Help() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 p-6" data-testid="help-page">
      <h2 className="text-lg font-semibold">Help</h2>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
        <h3 className="text-sm font-medium text-amber-400">What is this?</h3>
        <p className="mt-2 text-sm text-zinc-300">
          MiDashengLM-Gen MCP generates coherent 16 kHz mixed audio scenes - speech, music, sound
          effects, and environment - from structured text captions. The model is MiDashengLM-Gen
          (Xiaomi Research): an LLM backbone (Qwen3-1.7B) that autoregressively drives per-token
          flow matching. Everything runs locally on your GPU; weights are Apache-2.0.
        </p>
      </section>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
        <h3 className="text-sm font-medium text-amber-400">Structured caption format</h3>
        <p className="mt-2 text-sm text-zinc-300">
          Each scene is described by six tagged views. Absent views become{" "}
          <code className="rounded bg-zinc-800 px-1 text-amber-300">&lt;|unknown|&gt;</code>. You
          only need the caption view.
        </p>
        <pre className="mt-3 overflow-x-auto rounded-md bg-zinc-950 p-3 text-xs text-zinc-400">
          {`<|caption|> overall scene description
<|asr|> speech transcript
<|speech|> voice, emotion, style
<|sfx|> sound effects
<|music|> music description
<|env|> environment / ambience`}
        </pre>
        <p className="mt-2 text-xs text-zinc-500">
          For best speech intelligibility keep the asr view clean prose; make each view concrete and
          contrasting for richer scenes.
        </p>
      </section>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
        <h3 className="text-sm font-medium text-amber-400">Architecture & Ports</h3>
        <ul className="mt-2 space-y-1 text-sm text-zinc-300">
          <li>
            Backend: FastAPI + FastMCP HTTP on{" "}
            <code className="text-amber-300">127.0.0.1:11159</code> (REST /api, MCP streamable HTTP
            /mcp)
          </li>
          <li>
            Frontend: Vite dev server on <code className="text-amber-300">127.0.0.1:11160</code>
          </li>
          <li>
            Data: <code className="text-amber-300">data/</code> in the repo - SQLite index + scene
            WAV files
          </li>
          <li>Model cache: Hugging Face cache (shared with other transformers models)</li>
        </ul>
      </section>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
        <h3 className="text-sm font-medium text-amber-400">Environment variables</h3>
        <p className="mt-2 text-sm text-zinc-300">
          All settings are optional; see <code className="text-amber-300">.env.example</code> and{" "}
          <code className="text-amber-300">docs/CONFIGURATION.md</code>.
        </p>
      </section>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
        <h3 className="text-sm font-medium text-amber-400">Troubleshooting</h3>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-zinc-300">
          <li>
            <b>Model state "not_installed"</b>: run{" "}
            <code className="text-amber-300">uv sync --extra model</code> (torch + transformers).
          </li>
          <li>
            <b>Model state "model_missing"</b>: click Download Model in Settings, or run{" "}
            <code className="text-amber-300">just model-download</code>.
          </li>
          <li>
            <b>Generation is slow</b>: CPU inference is much slower than CUDA; check the GPU line on
            Settings.
          </li>
          <li>
            <b>Chat says no LLM</b>: start Ollama and check Settings - the Chat page uses your local
            Ollama instance.
          </li>
          <li>
            Full list: <code className="text-amber-300">docs/TROUBLESHOOTING.md</code>.
          </li>
        </ul>
      </section>
    </div>
  );
}
