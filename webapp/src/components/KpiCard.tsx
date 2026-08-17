interface Props {
  testid: string;
  label: string;
  value: string;
}

export default function KpiCard({ testid, label, value }: Props) {
  return (
    <div data-testid={testid} className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
      <div className="text-xs text-zinc-500">{label}</div>
      <div className="mt-1 truncate font-mono text-lg font-semibold text-zinc-100">{value}</div>
    </div>
  );
}
