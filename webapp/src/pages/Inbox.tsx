import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { type Job, api } from "../lib/api";

const STATUS_COLOR: Record<string, string> = {
  queued: "text-zinc-400",
  running: "text-amber-400",
  done: "text-green-400",
  failed: "text-red-400",
  interrupted: "text-yellow-400",
};

export default function Inbox() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await api.jobs(30);
      setJobs(data.items);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
    }
  }, []);

  useEffect(() => {
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, [load]);

  return (
    <div className="mx-auto max-w-4xl space-y-4 p-6" data-testid="inbox-page">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Generation Jobs</h2>
        <button
          type="button"
          onClick={load}
          className="flex items-center gap-1 rounded-md border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800"
          data-testid="inbox-refresh"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-md border border-red-800 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {jobs.length === 0 && (
        <div className="rounded-lg border border-dashed border-zinc-800 p-8 text-center text-sm text-zinc-500">
          No generation jobs yet. Submit one on the Generate page.
        </div>
      )}

      <div className="space-y-2">
        {jobs.map((job) => (
          <div
            key={job.id}
            className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-3"
            data-testid="job-card"
          >
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-zinc-400">{job.id}</span>
              <span className={`text-xs ${STATUS_COLOR[job.status] ?? "text-zinc-400"}`}>
                {job.status}
              </span>
            </div>
            <div className="mt-1 flex items-center gap-2 text-[11px] text-zinc-500">
              <span>{job.message}</span>
              {job.scene_id && <span className="text-amber-400">-&gt; {job.scene_id}</span>}
              {job.error && <span className="truncate text-red-400">{job.error}</span>}
            </div>
            <div className="mt-2 h-1 overflow-hidden rounded bg-zinc-800">
              <div
                className="h-full bg-amber-500 transition-all"
                style={{ width: `${Math.round((job.progress ?? 0) * 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
