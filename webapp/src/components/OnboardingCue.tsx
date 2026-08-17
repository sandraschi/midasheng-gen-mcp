import { AlertTriangle, Settings2 } from "lucide-react";
import type { ModelState } from "../lib/api";

interface Props {
  visible: boolean;
  state: ModelState;
  onAction: () => void;
}

const COPY: Record<ModelState, { title: string; body: string }> = {
  not_installed: {
    title: "Inference stack not installed",
    body: "Run 'uv sync --extra model' or start.ps1 to install torch + transformers (one time, ~3 GB).",
  },
  model_missing: {
    title: "Model checkpoint not downloaded",
    body: "Download the ~6 GB MiDashengLM-Gen checkpoint from Hugging Face to start generating.",
  },
  unloaded: {
    title: "Model ready to load",
    body: "The checkpoint is present but not in GPU memory. Load it from Settings, or just generate - it loads automatically.",
  },
  loading: { title: "Model loading...", body: "Loading the checkpoint onto the GPU." },
  ready: { title: "Model ready", body: "The model is loaded and ready to generate." },
  error: {
    title: "Model error",
    body: "The model failed to load. Check Settings for the error message and retry.",
  },
};

export default function OnboardingCue({ visible, state, onAction }: Props) {
  if (!visible) return null;
  const copy = COPY[state] ?? COPY.model_missing;
  return (
    <div
      data-testid="onboarding-cue"
      className="flex items-start gap-3 rounded-lg border border-red-800/60 bg-red-950/30 p-4"
    >
      <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
      <div className="flex-1">
        <div className="text-sm font-medium text-red-200">{copy.title}</div>
        <div className="mt-0.5 text-xs text-red-300/80">{copy.body}</div>
      </div>
      <button
        type="button"
        onClick={onAction}
        className="flex items-center gap-1 rounded-md bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-500"
      >
        <Settings2 className="h-3.5 w-3.5" />
        Go to Settings
      </button>
    </div>
  );
}
