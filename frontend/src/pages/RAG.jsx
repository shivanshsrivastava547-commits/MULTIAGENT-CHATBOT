// frontend/src/pages/RAG.jsx
import { useState, useRef } from 'react'
import { ingestFile, askRag } from '../services/api'
import { v4 as uuid } from 'uuid'
import ReactMarkdown from 'react-markdown'
import styles from './RAG.module.css'

export default function RAG() {
  const [threadId]              = useState(() => uuid())
  const [file, setFile]         = useState(null)
  const [ingesting, setIngesting] = useState(false)
  const [ingestResult, setIngestResult] = useState(null)
  const [query, setQuery]       = useState('')
  const [asking, setAsking]     = useState(false)
  const [answers, setAnswers]   = useState([])
  const [error, setError]       = useState(null)
  const fileRef                 = useRef(null)
  const dropRef                 = useRef(null)

  // ── Drag & drop ───────────────────────────────────────────────
  const onDrop = (e) => {
    e.preventDefault()
    dropRef.current?.classList.remove(styles.dragOver)
    const dropped = e.dataTransfer.files[0]
    if (dropped) setFile(dropped)
  }
  const onDragOver = (e) => {
    e.preventDefault()
    dropRef.current?.classList.add(styles.dragOver)
  }
  const onDragLeave = () => {
    dropRef.current?.classList.remove(styles.dragOver)
  }

  // ── Ingest ────────────────────────────────────────────────────
  const handleIngest = async () => {
    if (!file) return
    setIngesting(true)
    setError(null)
    try {
      const result = await ingestFile(file)
      setIngestResult(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setIngesting(false)
    }
  }

  // ── Ask ───────────────────────────────────────────────────────
  const handleAsk = async () => {
    if (!query.trim() || asking) return
    const currentQuery = query.trim()
    setAsking(true)
    setError(null)
    setQuery('')          // clear input so user can type next question
    try {
      const result = await askRag(currentQuery, threadId)
      setAnswers(prev => [...prev, { question: currentQuery, ...result }])
    } catch (err) {
      setError(err.message)
    } finally {
      setAsking(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAsk() }
  }

  return (
    <div className={styles.page}>
      <div className={styles.inner}>

        {/* Header */}
        <div className={styles.header}>
          <span className={styles.headerIcon}>⊞</span>
          <div>
            <h1 className={styles.title}>Document Intelligence</h1>
            <p className={styles.subtitle}>Upload a document, then ask questions about it</p>
          </div>
        </div>

        {/* Upload zone */}
        <div
          ref={dropRef}
          className={styles.dropZone}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onClick={() => fileRef.current?.click()}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.txt,.docx"
            style={{ display: 'none' }}
            onChange={e => setFile(e.target.files[0])}
          />
          {file ? (
            <div className={styles.fileSelected}>
              <span className={styles.fileIcon}>📄</span>
              <div>
                <p className={styles.fileName}>{file.name}</p>
                <p className={styles.fileSize}>{(file.size / 1024).toFixed(1)} KB</p>
              </div>
              <button
                className={styles.removeFile}
                onClick={e => { e.stopPropagation(); setFile(null); setIngestResult(null) }}
              >✕</button>
            </div>
          ) : (
            <div className={styles.dropPrompt}>
              <span className={styles.dropIcon}>⊕</span>
              <p className={styles.dropText}>Drop your file here or click to browse</p>
              <p className={styles.dropHint}>PDF · TXT · DOCX</p>
            </div>
          )}
        </div>

        {/* Ingest button */}
        {file && !ingestResult && (
          <button
            className={styles.ingestBtn}
            onClick={handleIngest}
            disabled={ingesting}
          >
            {ingesting ? (
              <><span className={styles.spinner} /> Processing document…</>
            ) : (
              <> Ingest document</>
            )}
          </button>
        )}

        {/* Ingest success */}
        {ingestResult && (
          <div className={styles.successBanner}>
            <span>✓</span>
            <span>
              <strong>{ingestResult.chunks}</strong> chunks ingested from{' '}
              <strong>{file?.name}</strong> — ready to answer questions
            </span>
          </div>
        )}

        {/* Ask section */}
        <div className={styles.askSection}>
          <div className={styles.inputRow}>
            <input
              className={styles.queryInput}
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Ask a question about your document…"
              disabled={asking}
            />
            <button
              className={`${styles.askBtn} ${query.trim() && !asking ? styles.askActive : ''}`}
              onClick={handleAsk}
              disabled={!query.trim() || asking}
            >
              {asking ? <span className={styles.spinner} /> : '→'}
            </button>
          </div>

          {/* Error */}
          {error && (
            <div className={styles.errorBanner}>
              <span>⚠</span> {error}
            </div>
          )}

          {/* Answer history */}
          {answers.map((a, idx) => (
            <div key={idx} className={styles.answerCard}>
              <div className={styles.questionRow}>
                <span className={styles.questionLabel}>Q</span>
                <span className={styles.questionText}>{a.question}</span>
              </div>
              <div className={styles.answerHeader}>
                <span className={styles.answerIcon}>◆</span>
                <span className={styles.answerLabel}>Answer</span>
              </div>
              <div className={styles.answerBody}>
                <ReactMarkdown>{a.answer}</ReactMarkdown>
              </div>
              {a.sources?.length > 0 && (
                <div className={styles.sources}>
                  <p className={styles.sourcesLabel}>Sources</p>
                  {a.sources.map((s, i) => (
                    <span key={i} className={styles.sourceTag}>{s}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

      </div>
    </div>
  )
}
