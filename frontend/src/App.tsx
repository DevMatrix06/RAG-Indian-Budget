import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, Database, Zap } from 'lucide-react'
import { SearchBar } from './components/SearchBar'
import { AnswerCard } from './components/AnswerCard'
import { LoadingSkeleton } from './components/LoadingSkeleton'
import { ParticleBackground } from './components/ParticleBackground'
import { queryDocumentsStream, type Source } from './lib/api'

type Status = 'idle' | 'loading' | 'streaming' | 'success' | 'error' | 'partial'

export default function App() {
  const [status, setStatus] = useState<Status>('idle')
  const [answer, setAnswer] = useState<string>('')
  const [sources, setSources] = useState<Source[]>([])
  const [error, setError] = useState<string | null>(null)
  const [lastQuestion, setLastQuestion] = useState<string>('')

  async function handleQuery(question: string) {
    setStatus('loading')
    setError(null)
    setAnswer('')
    setSources([])
    setLastQuestion(question)

    try {
      for await (const event of queryDocumentsStream(question)) {
        if (event.type === 'sources') {
          setSources(event.data)
          setStatus('streaming')
        } else if (event.type === 'token') {
          setAnswer((prev) => prev + event.text)
        } else if (event.type === 'error') {
          // Show whatever partial text arrived; if nothing yet, fall to full error
          setError(event.message)
          setStatus((prev) => (prev === 'streaming' ? 'partial' : 'error'))
        } else if (event.type === 'done') {
          setStatus('success')
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
      setStatus('error')
    }
  }

  const isLoading = status === 'loading' || status === 'streaming'
  const showAnswer = status === 'streaming' || status === 'success' || status === 'partial'

  return (
    <div className="min-h-screen bg-surface-950 font-sans text-zinc-100">
      {/* Three.js particle field */}
      <ParticleBackground />

      {/* Subtle grid overlay */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.025]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(99,102,241,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(99,102,241,0.8) 1px, transparent 1px)',
          backgroundSize: '48px 48px',
          zIndex: 1,
        }}
      />

      <div className="relative mx-auto max-w-2xl px-4 py-16 sm:py-24" style={{ zIndex: 2 }}>
        {/* Header */}
        <motion.div
          className="mb-10 text-center"
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        >
          <motion.div
            className="inline-flex items-center gap-2 px-3 py-1 mb-5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-xs font-medium"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1, duration: 0.3 }}
          >
            <Zap size={11} />
            RAG · Gemini · Qdrant
          </motion.div>

          <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight mb-3">
            <span className="bg-gradient-to-r from-indigo-400 via-violet-400 to-cyan-400 bg-clip-text text-transparent">
              Budget Document Search
            </span>
          </h1>
          <p className="text-zinc-400 text-sm leading-relaxed max-w-md mx-auto">
            Ask questions about Indian government budget documents 2026–27.
            Answers are grounded in retrieved source passages.
          </p>
        </motion.div>

        {/* Search */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.4, ease: 'easeOut' }}
        >
          <SearchBar onSubmit={handleQuery} loading={isLoading} />
        </motion.div>

        {/* Suggested queries */}
        <AnimatePresence>
          {status === 'idle' && (
            <motion.div
              className="mt-5"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ delay: 0.35, duration: 0.3 }}
            >
              <p className="text-xs text-zinc-600 mb-3 text-center">Try asking</p>
              <motion.div
                className="flex flex-wrap justify-center gap-2"
                variants={{ show: { transition: { staggerChildren: 0.07, delayChildren: 0.4 } } }}
                initial="hidden"
                animate="show"
              >
                {SUGGESTIONS.map((s) => (
                  <motion.button
                    key={s}
                    variants={{
                      hidden: { opacity: 0, y: 8 },
                      show:   { opacity: 1, y: 0 },
                    }}
                    whileHover={{ scale: 1.04 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => handleQuery(s)}
                    className="px-3 py-1.5 rounded-full border border-zinc-700/60 bg-surface-800 text-zinc-400 text-xs hover:border-zinc-600 hover:text-zinc-200 transition-colors duration-150"
                  >
                    {s}
                  </motion.button>
                ))}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <div className="mt-8 space-y-4">
          <AnimatePresence mode="wait">
            {status === 'loading' && (
              <motion.div
                key="skeleton"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <LoadingSkeleton />
              </motion.div>
            )}

            {status === 'error' && (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-start gap-3 p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 text-sm"
              >
                <AlertCircle size={16} className="shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium mb-0.5">Request failed</p>
                  <p className="text-red-400/80 text-xs">{error}</p>
                  <p className="text-red-400/60 text-xs mt-1">
                    Make sure the API server is running at localhost:8000
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {showAnswer && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs text-zinc-500">
                  <span className="text-zinc-300">"{lastQuestion}"</span>
                </p>
                {sources.length > 0 && (
                  <div className="flex items-center gap-1.5 text-xs text-zinc-500">
                    <Database size={11} />
                    {sources.length} chunk{sources.length !== 1 ? 's' : ''}
                  </div>
                )}
              </div>
              <AnswerCard
                answer={answer}
                sources={sources}
                streaming={status === 'streaming'}
              />
              {status === 'partial' && (
                <div className="mt-3 flex items-center gap-2 px-3 py-2 rounded-lg border border-amber-500/30 bg-amber-500/10 text-amber-400 text-xs">
                  <AlertCircle size={12} className="shrink-0" />
                  {error ?? 'Response timed out — try again'}
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}

const SUGGESTIONS = [
  'What is the total budget for 2026-27?',
  'What are the key budget documents?',
  'What is the Finance Commission grants allocation?',
  'Who presented the Finance Bill 2026?',
]
