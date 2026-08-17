import { Trash2 } from "lucide-react";
import type { Scene } from "../lib/api";

interface Props {
  scene: Scene;
  onDelete?: (id: string) => void;
}

export default function SceneCard({ scene, onDelete }: Props) {
  const caption = scene.caption?.caption ?? "(no caption)";
  const duration = scene.duration_seconds ? `${scene.duration_seconds.toFixed(1)}s` : "-";
  return (
    <div data-testid="scene-card" className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="truncate text-sm font-medium text-zinc-200">{caption}</div>
          <div className="mt-0.5 font-mono text-[11px] text-zinc-500">
            {scene.id} - {duration} - {new Date(scene.created_at).toLocaleString()}
          </div>
          {scene.caption?.asr && scene.caption.asr !== "<|unknown|>" && (
            <div className="mt-1 text-xs italic text-zinc-500">&quot;{scene.caption.asr}&quot;</div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <a
            href={scene.audio_url}
            download={`${scene.id}.wav`}
            data-testid="scene-download"
            className="rounded-md border border-zinc-700 p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
            title="Download WAV"
          >
            <DownloadIcon />
          </a>
          {onDelete && (
            <button
              type="button"
              onClick={() => onDelete(scene.id)}
              data-testid="scene-delete"
              className="rounded-md border border-zinc-700 p-1.5 text-zinc-400 hover:border-red-800 hover:bg-red-950/40 hover:text-red-300"
              title="Delete scene"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
      <audio controls preload="none" src={scene.audio_url} className="mt-3 w-full" />
    </div>
  );
}

function DownloadIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" x2="12" y1="15" y2="3" />
    </svg>
  );
}
