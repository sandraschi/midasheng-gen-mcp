import { Loader2, Play, Sparkles } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { type Job, type Sample, api } from "../lib/api";
import { useModel } from "../store/app";

interface FormState {
  caption: string;
  asr: string;
  speech: string;
  sfx: string;
  music: string;
  env: string;
  eval_cfg: number;
  stop_threshold: number;
  seed: string;
}

const EMPTY: FormState = {
  caption: "",
  asr: "",
  speech: "",
  sfx: "",
  music: "",
  env: "",
  eval_cfg: 2.0,
  stop_threshold: 0.5,
  seed: "",
};

const VIEWS: { key: keyof FormState; label: string; placeholder: string }[] = [
  {
    key: "caption",
    label: "Caption (overall scene)",
    placeholder:
      "A comedian delivering a punchline followed by crowd laughter and a jazz band sting",
  },
  {
    key: "asr",
    label: "ASR (speech transcript)",
    placeholder: "And that is why I never buy cheap luggage anymore!",
  },
  {
    key: "speech",
    label: "Speech (voice, emotion, style)",
    placeholder: "expressive comedic male voice",
  },
  { key: "sfx", label: "SFX (sound effects)", placeholder: "uproarious crowd laughter" },
  { key: "music", label: "Music", placeholder: "sudden upbeat jazz band sting" },
  { key: "env", label: "Environment / ambience", placeholder: "intimate comedy club" },
];

export default function Generate() {
  const [form, setForm] = useState<FormState>(EMPTY);
  const [samples, setSamples] = useState<Sample[]>([]);
  const [job, setJob] = useState<Job | null>(null);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const modelState = useModel((s) => s.state);

  const set = (key: keyof FormState, value: string | number) =>
    setForm((f) => ({ ...f, [key]: value }));

  useEffect(() => {
    api
      .samples()
      .then((d) => setSamples(d.samples))
      .catch(() => setSamples([]));
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const pollJob = useCallback(
    (id: string) => {
      stopPolling();
      pollRef.current = setInterval(async () => {
        try {
          const data = await api.job(id);
          setJob(data.job);
          if (data.job.status === "done") {
            stopPolling();
            setResultUrl(`/api/audio/${data.job.scene_id}`);
          } else if (data.job.status === "failed") {
            stopPolling();
            setError(data.job.error ?? "Generation failed");
          }
        } catch (e) {
          stopPolling();
          setError(e instanceof Error ? e.message : "Job poll failed");
        }
      }, 2000);
    },
    [stopPolling],
  );

  const submit = async () => {
    setError(null);
    setResultUrl(null);
    setJob(null);
    if (!form.caption.trim()) {
      setError("The caption view is required.");
      return;
    }
    try {
      const payload: Record<string, unknown> = {
        caption: form.caption,
        asr: form.asr || null,
        speech: form.speech || null,
        sfx: form.sfx || null,
        music: form.music || null,
        env: form.env || null,
        eval_cfg: form.eval_cfg,
        stop_threshold: form.stop_threshold,
        seed: form.seed ? Number(form.seed) : null,
      };
      const data = await api.generate(payload);
      pollJob(data.job_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Submission failed");
    }
  };

  const applySample = (s: Sample) => {
    setForm({
      ...EMPTY,
      caption: s.caption,
      asr: s.asr ?? "",
      speech: s.speech ?? "",
      sfx: s.sfx ?? "",
      music: s.music ?? "",
      env: s.env ?? "",
    });
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6 p-6" data-testid="generate-page">
      <div className="flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-amber-400" />
        <h2 className="text-lg font-semibold">Generate a Mixed Audio Scene</h2>
        <span
          className={`rounded-full px-2 py-0.5 text-[11px] ${
            modelState === "ready" ? "bg-green-500/10 text-green-400" : "bg-zinc-800 text-zinc-400"
          }`}
          data-testid="model-badge"
        >
          model: {modelState}
        </span>
      </div>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
        <h3 className="mb-3 text-sm font-medium text-zinc-300">Example Scenes</h3>
        <div className="flex flex-wrap gap-2" data-testid="example-prompts">
          {samples.map((s) => (
            <button
              type="button"
              key={s.id}
              onClick={() => applySample(s)}
              className="rounded-full border border-zinc-700 px-3 py-1 text-xs text-zinc-300 hover:border-amber-500 hover:text-amber-300"
              title={s.caption}
            >
              {s.id}
            </button>
          ))}
        </div>
      </section>

      <section className="space-y-4 rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
        {VIEWS.map(({ key, label, placeholder }) => (
          <div key={key}>
            <label
              htmlFor={`field-${key}`}
              className="mb-1 block text-xs font-medium text-zinc-400"
            >
              {label}
            </label>
            <textarea
              id={`field-${key}`}
              data-testid={`field-${key}`}
              value={String(form[key])}
              onChange={(e) => set(key, e.target.value)}
              placeholder={placeholder}
              rows={key === "caption" ? 3 : 2}
              className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:border-amber-500 focus:outline-none"
            />
          </div>
        ))}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label htmlFor="param-cfg" className="mb-1 block text-xs font-medium text-zinc-400">
              Guidance (eval_cfg): {form.eval_cfg.toFixed(1)}
            </label>
            <input
              id="param-cfg"
              type="range"
              min={0.5}
              max={5}
              step={0.1}
              value={form.eval_cfg}
              data-testid="param-cfg"
              onChange={(e) => set("eval_cfg", Number(e.target.value))}
              className="w-full accent-amber-500"
            />
          </div>
          <div>
            <label htmlFor="param-stop" className="mb-1 block text-xs font-medium text-zinc-400">
              Stop threshold: {form.stop_threshold.toFixed(2)}
            </label>
            <input
              id="param-stop"
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={form.stop_threshold}
              data-testid="param-stop"
              onChange={(e) => set("stop_threshold", Number(e.target.value))}
              className="w-full accent-amber-500"
            />
          </div>
          <div>
            <label htmlFor="param-seed" className="mb-1 block text-xs font-medium text-zinc-400">
              Seed (empty = random)
            </label>
            <input
              id="param-seed"
              type="number"
              value={form.seed}
              data-testid="param-seed"
              onChange={(e) => set("seed", e.target.value)}
              placeholder="42"
              className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-1.5 text-sm focus:border-amber-500 focus:outline-none"
            />
          </div>
        </div>

        {error && (
          <div
            className="rounded-md border border-red-800 bg-red-950/40 p-3 text-sm text-red-300"
            data-testid="generate-error"
          >
            {error}
          </div>
        )}

        <button
          type="button"
          onClick={submit}
          disabled={!!job && job.status === "running"}
          data-testid="generate-submit"
          className="flex items-center gap-2 rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-zinc-950 hover:bg-amber-400 disabled:opacity-50"
        >
          {job && job.status === "running" ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Generating...
            </>
          ) : (
            <>
              <Play className="h-4 w-4" /> Generate Scene
            </>
          )}
        </button>
      </section>

      {job && (
        <section
          className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4"
          data-testid="job-status"
        >
          <div className="flex items-center justify-between text-sm">
            <span className="font-mono text-zinc-400">{job.id}</span>
            <span
              className={
                job.status === "done"
                  ? "text-green-400"
                  : job.status === "failed"
                    ? "text-red-400"
                    : "text-amber-400"
              }
            >
              {job.status} - {job.message}
            </span>
          </div>
          <div className="mt-2 h-1.5 overflow-hidden rounded bg-zinc-800">
            <div
              className="h-full bg-amber-500 transition-all"
              style={{ width: `${Math.round((job.progress ?? 0) * 100)}%` }}
            />
          </div>
        </section>
      )}

      {resultUrl && (
        <section
          className="rounded-lg border border-green-800 bg-green-950/20 p-4"
          data-testid="generate-result"
        >
          <h3 className="mb-2 text-sm font-medium text-green-300">
            Scene generated - play it below
          </h3>
          <audio controls src={resultUrl} className="w-full" data-testid="result-audio" />
        </section>
      )}
    </div>
  );
}
