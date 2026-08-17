import { ExternalLink } from "lucide-react";

export default function ApiDocs() {
  const docsUrl = "http://127.0.0.1:11159/docs";
  return (
    <div className="flex h-full flex-col p-6" data-testid="api-docs-page">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold">API Docs</h2>
        <a
          href={docsUrl}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1 rounded-md border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800"
          data-testid="api-docs-open"
        >
          <ExternalLink className="h-3.5 w-3.5" /> Open in browser
        </a>
      </div>
      <div className="flex-1 overflow-hidden rounded-lg border border-zinc-800">
        <iframe
          src="/docs"
          title="Swagger UI"
          className="h-full w-full bg-white"
          data-testid="api-docs-iframe"
        />
      </div>
    </div>
  );
}
