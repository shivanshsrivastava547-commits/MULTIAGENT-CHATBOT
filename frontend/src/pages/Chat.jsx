// frontend/src/pages/Chat.jsx
import { useState, useRef, useEffect } from 'react'
import { useChat } from '../context/ChatContext'
import MessageBubble from '../components/MessageBubble'
import { streamMessage } from '../services/api'
import styles from './Chat.module.css'

const SUGGESTIONS = [
  'Explain how LangGraph works',
  'What is RAG and why is it useful?',
  'Write a Python function to sort a list',
  'Summarise the key ideas of transformers',
]

export default function Chat() {
  const { activeThread, newThread, messages, addMessage, updateLastMessage, renameThread } = useChat()
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const bottomRef               = useRef(null)
  const textareaRef             = useRef(null)

  const threadId  = activeThread
  const threadMsgs = messages[threadId] || []

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [threadMsgs])

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 160) + 'px'
  }, [input])

  const handleSend = async (text) => {
    const msg = (text || input).trim()
    if (!msg || loading) return

    let tid = threadId
    if (!tid) tid = newThread()

    setInput('')
    setLoading(true)

    // Add user message
    addMessage(tid, { role: 'user', content: msg })

    // Rename thread on first message
    if (threadMsgs.length === 0) {
      renameThread(tid, msg.slice(0, 36) + (msg.length > 36 ? '…' : ''))
    }

    // Add empty AI message placeholder
    addMessage(tid, { role: 'assistant', content: '', isStreaming: true })

    try {
      let full = ''
      for await (const chunk of streamMessage(msg, tid)) {
        full += chunk
        updateLastMessage(tid, full)
      }
      // Mark streaming done
      updateLastMessage(tid, full)
    } catch (err) {
      updateLastMessage(tid, `Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className={styles.page}>
      {/* Messages area */}
      <div className={styles.messages}>
        {threadMsgs.length === 0 ? (
          <div className={styles.empty}>
            <span className={styles.emptyIcon}>◆</span>
            <h2 className={styles.emptyTitle}>How can I help you today?</h2>
            <div className={styles.suggestions}>
              {SUGGESTIONS.map(s => (
                <button key={s} className={styles.suggestion} onClick={() => handleSend(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className={styles.messageList}>
            {threadMsgs.map((msg, i) => (
              <MessageBubble
                key={i}
                role={msg.role}
                content={msg.content}
                isStreaming={msg.isStreaming && i === threadMsgs.length - 1 && loading}
              />
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className={styles.inputWrap}>
        <div className={styles.inputBox}>
          <textarea
            ref={textareaRef}
            className={styles.textarea}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Message NexusAI…"
            rows={1}
            disabled={loading}
          />
          <button
            className={`${styles.sendBtn} ${(input.trim() && !loading) ? styles.sendActive : ''}`}
            onClick={() => handleSend()}
            disabled={!input.trim() || loading}
          >
            {loading ? <div className={styles.spinner} /> : '↑'}
          </button>
        </div>
        <p className={styles.hint}>Enter to send · Shift+Enter for new line</p>
      </div>
    </div>
  )
}
