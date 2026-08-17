import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/api";

interface LogEntry {
  ts: string;
  level: string;
  source: string;
  message: string;
}

export default function Logs() {
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [search, setSearch] = useState("");
  const [level, setLevel] = useState("");

  const load = useCallback(async () => {
    try {
      const data = await api.logs(search || undefined, level || undefined);
      setEntries(data.entries);
    } catch {
      /* backend unreachable */
    }
  }, [search, level]);

  useEffect(() => {
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, [load]);

  const color: Record<string, string> = {
    ERROR: "text-red-400",
    WARNING: "text-yellow-400",
    INFO: "text-zinc-400",
    DEBUG: "text-zinc-600",
  };

  return (
    <div className="mx-auto max-w-5xl space-y-3 p-6" data-testid="logs-page">
      <div className="flex items-center gap-2">
        <h2 className="text-lg font-semibold">Logs</h2>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search logs..."
          className="ml-auto w-64 rounded-md border border-zinc-700 bg-zinc-950 px-3 py-1.5 text-sm focus:border-amber-500 focus:outline-none"
        />
        <select
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          className="rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm text-zinc-200"
        >
          <option value="">all levels</option>
          <option value="ERROR">ERROR</option>
          <option value="WARNING">WARNING</option>
          <option value="INFO">INFO</option>
          <option value="DEBUG">DEBUG</option>
        </select>
        <button
          type="button"
          onClick={load}
          className="flex items-center gap-1 rounded-md border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800"
        >
          <RefreshCw className="h-3.5 w-3.5" />
        </button>
      </div>

      <div className="overflow-auto rounded-lg border border-zinc-800 bg-zinc-950">
        <table className="w-full text-left font-mono text-xs">
          <thead className="sticky top-0 bg-zinc-900 text-zinc-500">
            <tr>
              <th className="px-3 py-2">time</th>
              <th className="px-3 py-2">level</th>
              <th className="px-3 py-2">source</th>
              <th className="px-3 py-2">message</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e) => (
              <tr key={`${e.ts}-${e.source}-${e.message}`} className="border-t border-zinc-800/60">
                <td className="whitespace-nowrap px-3 py-1.5 text-zinc-500">
                  {new Date(e.ts).toLocaleTimeString()}
                </td>
                <td className={`px-3 py-1.5 ${color[e.level] ?? "text-zinc-400"}`}>{e.level}</td>
                <td className="px-3 py-1.5 text-zinc-500">{e.source}</td>
                <td className="px-3 py-1.5 text-zinc-300">{e.message}</td>
              </tr>
            ))}
            {entries.length === 0 && (
              <tr>
                <td colSpan={4} className="px-3 py-6 text-center text-zinc-600">
                  No log entries.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
