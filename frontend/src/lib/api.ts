const API_BASE = ''  // All requests go through the Vite proxy → localhost:8000

export interface Source {
  text: string
  source: string
  page: number
  chunk_index: number
  score: number
}

export interface QueryResponse {
  answer: string
  sources: Source[]
}

export type StreamEvent =
  | { type: 'sources'; data: Source[] }
  | { type: 'token'; text: string }
  | { type: 'error'; message: string }
  | { type: 'done' }

export async function queryDocuments(
  question: string,
  top_k = 5,
): Promise<QueryResponse> {
  const res = await fetch(`${API_BASE}/query/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `Request failed: ${res.status}`)
  }

  return res.json()
}

export async function* queryDocumentsStream(
  question: string,
  top_k = 5,
): AsyncGenerator<StreamEvent> {
  const res = await fetch(`${API_BASE}/query/stream/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `Request failed: ${res.status}`)
  }
  if (!res.body) throw new Error('No response body from server')

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const payload = line.slice(6).trim()
      if (payload === '[DONE]') {
        yield { type: 'done' }
        return
      }
      try {
        yield JSON.parse(payload) as StreamEvent
      } catch {
        // skip malformed SSE lines
      }
    }
  }
}
