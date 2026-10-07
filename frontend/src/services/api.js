// frontend/src/services/api.js
// In production (Render), VITE_API_URL is set to the backend service URL.
// In local dev, falls back to '/api' which Vite proxies to localhost:8000.
const BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api'

// ── Chat ──────────────────────────────────────────────────────────
export async function sendMessage(message, threadId) {
  const res = await fetch(`${BASE}/chat`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ message, thread_id: threadId }),
  })
  if (!res.ok) throw new Error(`Chat error: ${res.status}`)
  return res.json()   // { response, thread_id }
}

// ── Chat streaming ────────────────────────────────────────────────
export async function* streamMessage(message, threadId) {
  const res = await fetch(`${BASE}/chat/stream`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ message, thread_id: threadId }),
  })
  if (!res.ok) throw new Error(`Stream error: ${res.status}`)

  const reader  = res.body.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const text = decoder.decode(value)
    const lines = text.split('\n').filter(l => l.startsWith('data: '))
    for (const line of lines) {
      const raw = line.slice('data: '.length).trim()
      if (raw === '[DONE]' || raw === '') continue
      try {
        yield JSON.parse(raw)   // decode escaped newlines (\n → actual newline)
      } catch {
        yield raw               // fallback: yield as-is if not valid JSON
      }
    }
  }
}

// ── Threads ───────────────────────────────────────────────────────
export async function fetchThreads() {
  const res = await fetch(`${BASE}/threads`)
  if (!res.ok) throw new Error(`Threads error: ${res.status}`)
  const data = await res.json()
  return data.threads   // string[]
}

// ── RAG: ingest ───────────────────────────────────────────────────
export async function ingestFile(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/rag/ingest`, {
    method: 'POST',
    body:   form,
  })
  if (!res.ok) throw new Error(`Ingest error: ${res.status}`)
  return res.json()   // { file, chunks, message }
}

// ── RAG: ask ──────────────────────────────────────────────────────
export async function askRag(query, threadId) {
  const res = await fetch(`${BASE}/rag`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ query, thread_id: threadId }),
  })
  if (!res.ok) throw new Error(`RAG error: ${res.status}`)
  return res.json()   // { answer, sources, thread_id }
}

// ── Research ──────────────────────────────────────────────────────
export async function runResearch(query) {
  const res = await fetch(`${BASE}/research`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ query }),
  })
  if (!res.ok) throw new Error(`Research error: ${res.status}`)
  return res.json()
}
