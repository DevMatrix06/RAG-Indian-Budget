import { Suspense } from 'react'
import { motion } from 'framer-motion'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { BookOpen, RefreshCw } from 'lucide-react'
import { type Source } from '../lib/api'
import { CitationChip } from './CitationChip'

interface Props {
  answer: string
  sources: Source[]
  streaming?: boolean
}

const chipVariants = {
  hidden: { opacity: 0, scale: 0.75 },
  show:   { opacity: 1, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 22 } },
}

export function AnswerCard({ answer, sources, streaming = false }: Props) {
  const uniqueSources = sources.filter(
    (s, i, arr) =>
      arr.findIndex((x) => x.source === s.source && x.page === s.page) === i,
  )

  const isEmpty = !streaming && answer.trim() === ''

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="w-full rounded-2xl border border-zinc-700/50 bg-surface-900 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-5 py-3.5 border-b border-zinc-700/40 bg-surface-800/60">
        <BookOpen size={14} className="text-indigo-400 shrink-0" />
        <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">Answer</span>
        {streaming && (
          <span className="ml-auto inline-block h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse" />
        )}
      </div>

      {/* Body */}
      <div className="px-5 py-5 min-h-[48px]">
        {isEmpty ? (
          <div className="flex items-center gap-2 text-zinc-500 text-sm">
            <RefreshCw size={13} />
            No response received — please try again
          </div>
        ) : (
          <Suspense fallback={<span className="text-zinc-400 text-sm">Rendering…</span>}>
            <div className="prose prose-sm prose-invert max-w-none
              prose-p:text-zinc-200 prose-p:leading-relaxed
              prose-strong:text-white prose-strong:font-semibold
              prose-headings:text-zinc-50
              prose-ul:text-zinc-200 prose-ol:text-zinc-200 prose-li:text-zinc-200
              prose-code:text-indigo-300 prose-code:bg-indigo-950/60 prose-code:rounded prose-code:px-1 prose-code:before:content-none prose-code:after:content-none
              prose-pre:bg-zinc-900 prose-pre:border prose-pre:border-zinc-700/60
              prose-blockquote:border-indigo-500/50 prose-blockquote:text-zinc-400">
              <Markdown remarkPlugins={[remarkGfm]}>{answer}</Markdown>
              {streaming && (
                <span className="not-prose inline-block w-0.5 h-[1em] bg-indigo-400 animate-pulse align-text-bottom ml-0.5" />
              )}
            </div>
          </Suspense>
        )}
      </div>

      {/* Sources */}
      {uniqueSources.length > 0 && (
        <div className="px-5 pb-5">
          <p className="text-[11px] uppercase tracking-wider text-zinc-500 mb-2.5 font-medium">
            Sources — {uniqueSources.length} chunk{uniqueSources.length > 1 ? 's' : ''} retrieved
          </p>
          <motion.div
            className="flex flex-wrap gap-2"
            variants={{ show: { transition: { staggerChildren: 0.06, delayChildren: 0.1 } } }}
            initial="hidden"
            animate="show"
          >
            {uniqueSources.map((s, i) => (
              <motion.div key={`${s.source}-${s.page}-${i}`} variants={chipVariants}>
                <CitationChip source={s.source} page={s.page} score={s.score} />
              </motion.div>
            ))}
          </motion.div>
        </div>
      )}
    </motion.div>
  )
}
