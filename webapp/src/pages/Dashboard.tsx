import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import KpiCard from "../components/KpiCard";
import OnboardingCue from "../components/OnboardingCue";
import SceneCard from "../components/SceneCard";
import { type DashboardData, type Scene, api } from "../lib/api";
import { useModel } from "../store/app";

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const modelState = useModel((s) => s.state);
  const refreshModel = useModel((s) => s.refresh);

  const load = useCallback(async () => {
    try {
      setData(await api.dashboard());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Dashboard load failed");
    }
  }, []);

  useEffect(() => {
    load();
    refreshModel();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, [load, refreshModel]);

  const needsOnboarding = modelState === "model_missing" || modelState === "not_installed";

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6" data-testid="dashboard">
      <section className="rounded-xl border border-zinc-800 bg-gradient-to-br from-zinc-900 to-zinc-950 p-8">
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-bold">MiDashengLM-Gen</h2>
          <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-xs text-amber-400">
            Audio Scene Studio
          </span>
        </div>
        <p className="mt-2 max-w-2xl text-sm text-zinc-400">
          Generate coherent 16 kHz mixed audio scenes - speech, music, sound effects, and ambience -
          from text with the MiDashengLM-Gen model (LLM-driven autoregressive flow matching, running
          on your GPU).
        </p>
        <div className="mt-4 flex gap-3">
          <Link
            to="/generate"
            data-testid="cta-generate"
            className="rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-zinc-950 hover:bg-amber-400"
          >
            Generate a Scene
          </Link>
          <Link
            to="/scenes"
            className="rounded-md border border-zinc-700 px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-800"
          >
            Browse Library
          </Link>
        </div>
      </section>

      <OnboardingCue
        visible={needsOnboarding}
        state={modelState}
        onAction={() => {
          window.location.hash = "#/settings";
        }}
      />

      {error && (
        <div className="rounded-md border border-red-800 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <section className="grid grid-cols-2 gap-4 lg:grid-cols-4" data-testid="kpi-grid">
        <KpiCard
          testid="kpi-scenes"
          label="Scenes Generated"
          value={data ? String(data.scene_count) : "-"}
        />
        <KpiCard
          testid="kpi-seconds"
          label="Total Audio"
          value={data ? `${data.total_seconds.toFixed(1)}s` : "-"}
        />
        <KpiCard testid="kpi-model" label="Model" value={modelState} />
        <KpiCard
          testid="kpi-gpu"
          label="Device"
          value={data?.gpu_name ? data.gpu_name : (data?.device ?? "-")}
        />
      </section>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-medium text-zinc-300">Recent Scenes</h3>
          <Link to="/scenes" className="text-xs text-amber-400 hover:underline">
            View all
          </Link>
        </div>
        <div className="space-y-3">
          {data && data.recent.length === 0 && (
            <div className="rounded-lg border border-dashed border-zinc-800 p-6 text-center text-sm text-zinc-500">
              No scenes yet.{" "}
              <Link to="/generate" className="text-amber-400 hover:underline">
                Generate your first one
              </Link>
              .
            </div>
          )}
          {data?.recent.map((scene: Scene) => (
            <SceneCard key={scene.id} scene={scene} />
          ))}
        </div>
      </section>
    </div>
  );
}
