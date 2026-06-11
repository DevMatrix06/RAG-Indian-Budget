export function LoadingSkeleton() {
  return (
    <div className="w-full rounded-2xl border border-zinc-700/50 bg-surface-900 overflow-hidden animate-pulse">
      <div className="flex items-center gap-2 px-5 py-3.5 border-b border-zinc-700/40 bg-surface-800/60">
        <div className="h-3 w-3 rounded bg-zinc-700" />
        <div className="h-3 w-16 rounded bg-zinc-700" />
      </div>
      <div className="px-5 py-5 space-y-2.5">
        <div className="h-3.5 w-full rounded bg-zinc-800" />
        <div className="h-3.5 w-5/6 rounded bg-zinc-800" />
        <div className="h-3.5 w-4/6 rounded bg-zinc-800" />
        <div className="h-3.5 w-full rounded bg-zinc-800" />
        <div className="h-3.5 w-3/5 rounded bg-zinc-800" />
      </div>
      <div className="px-5 pb-5 space-y-2">
        <div className="h-2.5 w-24 rounded bg-zinc-800" />
        <div className="flex gap-2">
          <div className="h-6 w-32 rounded-full bg-zinc-800" />
          <div className="h-6 w-28 rounded-full bg-zinc-800" />
          <div className="h-6 w-36 rounded-full bg-zinc-800" />
        </div>
      </div>
    </div>
  )
}
