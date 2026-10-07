// frontend/src/pages/Research.jsx
import { useState } from 'react'
import { runResearch } from '../services/api'
import ReactMarkdown from 'react-markdown'
import styles from './Research.module.css'

export default function Research() {
  const [query,    setQuery]   = useState('')
  const [loading,  setLoading] = useState(false)
  const [results,  setResults] = useState([])   // history of all research results
  const [error,    setError]   = useState(null)

  const handleResearch = async () => {
    if (!query.trim() || loading) return
    const currentQuery = query.trim()
    setLoading(true)
    setError(null)
    setQuery('')          // clear input for next question
    try {
      const data = await runResearch(currentQuery)
      setResults(prev => [...prev, { query: currentQuery, ...data }])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter') handleResearch()
  }

  const scoreColor = (score) => {
    if (score >= 8) return styles.scoreGreen
    if (score >= 6) return styles.scoreAmber
    return styles.scoreRed
  }

  return (
    <div className={styles.page}>
      <div className={styles.inner}>

        {/* Header */}
        <div className={styles.header}>
          <span className={styles.headerIcon}>⊹</span>
          <div>
            <h1 className={styles.title}>Deep Research</h1>
            <p className={styles.subtitle}>AI searches the web, writes a summary, then self-critiques</p>
          </div>
        </div>

        {/* Pipeline indicator */}
        <div className={styles.pipeline}>
          {['Search web', 'Summarise', 'Critique', 'Score'].map((step, i) => (
            <div key={step} className={styles.pipelineStep}>
              <div className={`${styles.stepDot} ${loading ? styles.stepActive : ''}`}
                style={{ animationDelay: `${i * 0.2}s` }}
              />
              <span className={styles.stepLabel}>{step}</span>
              {i < 3 && <span className={styles.stepArrow}>→</span>}
            </div>
          ))}
        </div>

        {/* Input */}
        <div className={styles.inputRow}>
          <input
            className={styles.input}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKey}
            placeholder="What do you want to research?"
            disabled={loading}
          />
          <button
            className={`${styles.btn} ${query.trim() && !loading ? styles.btnActive : ''}`}
            onClick={handleResearch}
            disabled={!query.trim() || loading}
          >
            {loading ? <span className={styles.spinner} /> : 'Research →'}
          </button>
        </div>

        {loading && (
          <div className={styles.loadingState}>
            <div className={styles.loadingDots}>
              <span /><span /><span />
            </div>
            <p className={styles.loadingText}>Searching and analysing… this takes ~30 seconds</p>
          </div>
        )}

        {error && (
          <div className={styles.errorBanner}>⚠ {error}</div>
        )}

        {/* Research history — newest at bottom */}
        {results.map((item, idx) => (
          <div key={idx} className={styles.results}>

            {/* Query label */}
            <div className={styles.queryLabel}>
              <span className={styles.queryBadge}>Q</span>
              <span className={styles.queryText}>{item.query}</span>
            </div>

            {/* Summary */}
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <span className={styles.cardIcon}>◆</span>
                <span className={styles.cardTitle}>Research Summary</span>
                <span className={`${styles.verdict} ${item.passed ? styles.verdictPass : styles.verdictFail}`}>
                  {item.passed ? '✓ PASS' : '✗ FAIL'}
                </span>
                {item.attempts > 1 && (
                  <span className={styles.attempts}>{item.attempts} attempts</span>
                )}
              </div>
              <div className={styles.cardBody}>
                <ReactMarkdown>{item.summary}</ReactMarkdown>
              </div>
            </div>

            {/* Critique scores */}
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <span className={styles.cardIcon}>⊹</span>
                <span className={styles.cardTitle}>Quality Critique</span>
                <span className={`${styles.overallScore} ${scoreColor(item.critique.overall_score)}`}>
                  {item.critique.overall_score}/10
                </span>
              </div>
              <div className={styles.cardBody}>
                <div className={styles.scores}>
                  {Object.entries(item.critique.scores).map(([key, val]) => (
                    <div key={key} className={styles.scoreRow}>
                      <span className={styles.scoreKey}>{key.replace('_', ' ')}</span>
                      <div className={styles.scoreBar}>
                        <div
                          className={styles.scoreBarFill}
                          style={{ width: `${val * 10}%`, opacity: 0.5 + val * 0.05 }}
                        />
                      </div>
                      <span className={styles.scoreVal}>{val}/10</span>
                    </div>
                  ))}
                </div>
                <div className={styles.feedback}>
                  <p className={styles.feedbackLabel}>Feedback</p>
                  <p className={styles.feedbackText}>{item.critique.feedback}</p>
                </div>
                <div className={styles.swRow}>
                  {item.critique.strengths?.length > 0 && (
                    <div className={styles.swBox}>
                      <p className={styles.swLabel}>Strengths</p>
                      {item.critique.strengths.map((s, i) => (
                        <p key={i} className={styles.swItem}>+ {s}</p>
                      ))}
                    </div>
                  )}
                  {item.critique.weaknesses?.length > 0 && (
                    <div className={styles.swBox}>
                      <p className={styles.swLabel}>Weaknesses</p>
                      {item.critique.weaknesses.map((w, i) => (
                        <p key={i} className={styles.swItem}>− {w}</p>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

          </div>
        ))}
      </div>
    </div>
  )
}
