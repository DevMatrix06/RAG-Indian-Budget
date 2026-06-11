import { useState, type FormEvent } from 'react'
import { motion } from 'framer-motion'
import { Search, Loader2 } from 'lucide-react'
import { cn } from '../lib/utils'

interface Props {
  onSubmit: (question: string) => void
  loading: boolean
}

export function SearchBar({ onSubmit, loading }: Props) {
  const [value, setValue] = useState('')
  const [focused, setFocused] = useState(false)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const q = value.trim()
    if (q && !loading) onSubmit(q)
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative flex items-center gap-3">
        {/* Input with animated glow wrapper */}
        <motion.div
          className="relative flex-1 rounded-xl"
          animate={{
            boxShadow: focused
              ? '0 0 0 2px rgba(99,102,241,0.4), 0 0 28px rgba(99,102,241,0.12)'
              : '0 0 0 0px rgba(99,102,241,0)',
          }}
          transition={{ duration: 0.2 }}
        >
          <Search
            size={16}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 pointer-events-none z-10"
          />
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder="Ask a question about the budget documents…"
            disabled={loading}
            className={cn(
              'w-full pl-11 pr-4 py-3.5 rounded-xl text-sm',
              'bg-surface-800 border border-zinc-700/60',
              'text-zinc-100 placeholder:text-zinc-500',
              'focus:outline-none focus:border-indigo-500/50',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'transition-colors duration-200',
            )}
          />
        </motion.div>

        {/* Button */}
        <motion.button
          type="submit"
          disabled={loading || !value.trim()}
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          className={cn(
            'flex items-center gap-2 px-5 py-3.5 rounded-xl text-sm font-medium',
            'bg-indigo-600 text-white',
            'hover:bg-indigo-500 active:bg-indigo-700',
            'disabled:opacity-40 disabled:cursor-not-allowed',
            'transition-colors duration-200 shrink-0',
          )}
        >
          {loading ? (
            <>
              <Loader2 size={15} className="animate-spin" />
              Searching…
            </>
          ) : (
            'Search'
          )}
        </motion.button>
      </div>
    </form>
  )
}
