import {
  AudioLines,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  FileCode2,
  Inbox,
  ListMusic,
  MessageSquare,
  Play,
  Settings,
  Sparkles,
  Terminal,
  Wrench,
} from "lucide-react";
// AppLayout: retractable sidebar + fixed topbar (WEBAPP_SOTA section II).
import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

import { useBackend } from "./store/app";

const NAV = [
  { to: "/", label: "Dashboard", icon: Sparkles },
  { to: "/generate", label: "Generate", icon: Play },
  { to: "/scenes", label: "Scenes", icon: ListMusic },
  { to: "/inbox", label: "Inbox", icon: Inbox },
  { to: "/tools", label: "Tools", icon: Wrench },
  { to: "/skills", label: "Skills", icon: BookOpen },
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/settings", label: "Settings", icon: Settings },
  { to: "/help", label: "Help", icon: AudioLines },
  { to: "/logs", label: "Logs", icon: Terminal },
  { to: "/api-docs", label: "API Docs", icon: FileCode2 },
];

const TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/generate": "Generate Scene",
  "/scenes": "Scene Library",
  "/inbox": "Inbox - Generation Jobs",
  "/tools": "MCP Tools",
  "/skills": "Skills",
  "/chat": "Chat",
  "/settings": "Settings",
  "/help": "Help",
  "/logs": "Logs",
  "/api-docs": "API Docs",
};

export default function Layout() {
  const [collapsed, setCollapsed] = useState(false);
  const backendOk = useBackend((s) => s.ok);
  const refresh = useBackend((s) => s.refresh);
  const location = useLocation();
  const title = TITLES[location.pathname] ?? "MiDashengLM-Gen";

  // Exponential backoff health poll: 1s, 2s, 4s, 8s, 16s
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    let delay = 1000;
    let cancelled = false;
    const poll = async () => {
      await refresh();
      if (cancelled) return;
      delay = backendOk === false ? Math.min(delay * 2, 16000) : 10000;
      timer = setTimeout(poll, delay);
    };
    poll();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [refresh, backendOk]);

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100">
      <aside
        data-testid="sidebar"
        className={`flex flex-col border-r border-zinc-800 bg-zinc-900/60 backdrop-blur transition-all ${
          collapsed ? "w-16" : "w-56"
        }`}
      >
        <div className="flex items-center gap-2 px-3 py-4">
          <AudioLines className="h-7 w-7 shrink-0 text-amber-500" />
          {!collapsed && (
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold">MiDashengLM-Gen</div>
              <div className="text-[10px] text-zinc-500">v0.1.0</div>
            </div>
          )}
        </div>

        <button
          type="button"
          onClick={() => setCollapsed((c) => !c)}
          className="mx-2 mb-2 flex w-fit items-center gap-1 rounded-md px-2 py-1 text-xs text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          data-testid="sidebar-toggle"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          {!collapsed && "Collapse"}
        </button>

        <nav className="flex-1 space-y-1 overflow-y-auto px-2">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              aria-label={label}
              data-testid={`nav-${label.toLowerCase()}`}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors ${
                  isActive
                    ? "bg-amber-500/10 text-amber-400"
                    : "text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
                }`
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              {!collapsed && label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-zinc-800 p-3">
          <div className="flex items-center gap-2 text-xs" data-testid="backend-dot">
            <span
              className={`h-2 w-2 rounded-full ${
                backendOk === null
                  ? "animate-pulse bg-zinc-500"
                  : backendOk
                    ? "bg-green-500"
                    : "bg-red-500"
              }`}
            />
            <span className="text-zinc-400">
              {backendOk === null ? "Connecting..." : backendOk ? "Connected" : "Offline"}
            </span>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-12 items-center justify-between border-b border-zinc-800 bg-zinc-900/40 px-4">
          <h1 className="text-sm font-medium" data-testid="page-title">
            {title}
          </h1>
          <div className="flex items-center gap-3 text-xs text-zinc-500">
            <span>backend :11159</span>
            <span>frontend :11160</span>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
