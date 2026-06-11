import { FileText } from 'lucide-react'
import { cn } from '../lib/utils'

interface Props {
  source: string
  page: number
  score: number
}

function scoreColor(score: number) {
  if (score >= 0.75) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
  if (score >= 0.65) return 'text-amber-400 border-amber-500/30 bg-amber-500/10'
  return 'text-red-400 border-red-500/30 bg-red-500/10'
}

export function CitationChip({ source, page, score }: Props) {
  // Strip extension for display
  const label = source.replace(/\.pdf$/i, '')

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full',
        'border text-xs font-medium font-mono',
        'bg-surface-800 border-zinc-700/60 text-zinc-300',
        'transition-colors duration-150',
      )}
      title={`Similarity score: ${score.toFixed(3)}`}
    >
      <FileText size={11} className="shrink-0 text-zinc-500" />
      <span className="truncate max-w-[160px]">{label}</span>
      <span className="text-zinc-500">p{page}</span>
      <span
        className={cn(
          'ml-1 px-1.5 py-0.5 rounded-full text-[10px] border',
          scoreColor(score),
        )}
      >
        {score.toFixed(2)}
      </span>
    </div>
  )
}
