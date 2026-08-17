import { Eraser, Send } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useChat } from "../store/llm";

export default function Chat() {
  const personality = useChat((s) => s.personalityId);
  const personalities = useChat((s) => s.personalities);
  const messages = useChat((s) => s.messages);
  const sending = useChat((s) => s.sending);
  const error = useChat((s) => s.error);
  const send = useChat((s) => s.send);
  const clear = useChat((s) => s.clear);
  const setPersonality = useChat((s) => s.setPersonality);
  const restore = useChat((s) => s.restore);
  const [input, setInput] = useState("");
  const [customPrompt, setCustomPrompt] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    restore();
  }, [restore]);

  // biome-ignore lint/correctness/useExhaustiveDependencies: messages/sending intentionally trigger the scroll
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, sending]);

  const submit = () => {
    const text = input.trim();
    if (!text || sending) return;
    setInput("");
    void send(text, customPrompt);
  };

  return (
    <div className="mx-auto flex h-full max-w-4xl flex-col p-6" data-testid="chat-page">
      <div className="mb-3 flex flex-wrap items-center gap-2" data-testid="chat-controls">
        <select
          value={personality}
          onChange={(e) => setPersonality(e.target.value)}
          data-testid="personality-select"
          className="rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-xs text-zinc-200 focus:border-amber-500 focus:outline-none"
        >
          {personalities.map((p) => (
            <option key={p.id} value={p.id}>
              {p.label}
            </option>
          ))}
        </select>
        {personality === "custom" && (
          <textarea
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder="Custom system prompt..."
            rows={1}
            className="min-w-64 flex-1 rounded-md border border-zinc-700 bg-zinc-950 px-2 py-1.5 text-xs focus:border-amber-500 focus:outline-none"
          />
        )}
        <button
          type="button"
          onClick={clear}
          disabled={messages.length === 0}
          data-testid="chat-clear"
          className="flex items-center gap-1 rounded-md border border-zinc-700 px-2 py-1.5 text-xs text-zinc-400 hover:bg-zinc-800 disabled:opacity-40"
        >
          <Eraser className="h-3.5 w-3.5" /> Clear
        </button>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 space-y-4 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-900/40 p-4"
        data-testid="chat-messages"
      >
        {messages.length === 0 && (
          <div className="py-10 text-center text-sm text-zinc-500">
            Ask about prompt design, caption views, or how the model works. The chat uses your local
            Ollama instance - configure it in Settings.
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={m.ts ?? `msg-${i}`}
            className={`max-w-[85%] whitespace-pre-wrap rounded-lg p-3 text-sm ${
              m.role === "user"
                ? "ml-auto bg-amber-500/15 text-amber-100"
                : "bg-zinc-800 text-zinc-200"
            }`}
          >
            {m.content}
          </div>
        ))}
        {sending && (
          <div className="max-w-[85%] rounded-lg bg-zinc-800 p-3 text-sm text-zinc-400">
            Thinking...
          </div>
        )}
        {error && (
          <div className="rounded-lg border border-red-800 bg-red-950/40 p-3 text-sm text-red-300">
            {error}
          </div>
        )}
      </div>

      <div className="mt-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Ask about audio scene generation..."
          data-testid="chat-input"
          className="flex-1 rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:border-amber-500 focus:outline-none"
        />
        <button
          type="button"
          onClick={submit}
          disabled={sending || !input.trim()}
          data-testid="chat-send"
          className="flex items-center gap-1 rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-zinc-950 hover:bg-amber-400 disabled:opacity-50"
        >
          <Send className="h-4 w-4" /> Send
        </button>
      </div>
    </div>
  );
}
