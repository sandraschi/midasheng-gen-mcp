import { ChevronLeft, ChevronRight } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import SceneCard from "../components/SceneCard";
import { type Scene, api } from "../lib/api";

const PAGE_SIZE = 10;

export default function Scenes() {
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const page = await api.scenes(PAGE_SIZE, offset);
      setScenes(page.items);
      setTotal(page.total);
      setHasMore(page.has_more);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Load failed");
    }
  }, [offset]);

  useEffect(() => {
    load();
  }, [load]);

  const del = async (id: string) => {
    if (!window.confirm(`Delete scene ${id}? This removes the WAV file.`)) return;
    try {
      await api.deleteScene(id);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-4 p-6" data-testid="scenes-page">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Scene Library</h2>
        <span className="text-xs text-zinc-500">{total} scenes</span>
      </div>

      {error && (
        <div className="rounded-md border border-red-800 bg-red-950/40 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {scenes.length === 0 && !error && (
        <div className="rounded-lg border border-dashed border-zinc-800 p-8 text-center text-sm text-zinc-500">
          No scenes in the library yet.
        </div>
      )}

      <div className="space-y-3">
        {scenes.map((scene) => (
          <SceneCard key={scene.id} scene={scene} onDelete={del} />
        ))}
      </div>

      <div className="flex items-center justify-between pt-2">
        <button
          type="button"
          onClick={() => setOffset((o) => Math.max(0, o - PAGE_SIZE))}
          disabled={offset === 0}
          className="flex items-center gap-1 rounded-md border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800 disabled:opacity-40"
          data-testid="scenes-prev"
        >
          <ChevronLeft className="h-3.5 w-3.5" /> Prev
        </button>
        <span className="text-xs text-zinc-500">
          {offset + 1}-{Math.min(offset + PAGE_SIZE, total)} of {total}
        </span>
        <button
          type="button"
          onClick={() => setOffset((o) => o + PAGE_SIZE)}
          disabled={!hasMore}
          className="flex items-center gap-1 rounded-md border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800 disabled:opacity-40"
          data-testid="scenes-next"
        >
          Next <ChevronRight className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
