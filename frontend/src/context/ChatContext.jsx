// frontend/src/context/ChatContext.jsx
import { createContext, useContext, useState, useCallback } from 'react'
import { v4 as uuid } from 'uuid'

const ChatContext = createContext(null)

export function ChatProvider({ children }) {
  const [threads, setThreads]       = useState([])
  const [activeThread, setActive]   = useState(null)
  const [messages, setMessages]     = useState({})  // threadId → msg[]

  const newThread = useCallback(() => {
    const id = uuid()
    setThreads(prev => [{ id, label: 'New chat' }, ...prev])
    setActive(id)
    setMessages(prev => ({ ...prev, [id]: [] }))
    return id
  }, [])

  const addMessage = useCallback((threadId, msg) => {
    setMessages(prev => ({
      ...prev,
      [threadId]: [...(prev[threadId] || []), msg],
    }))
  }, [])

  const updateLastMessage = useCallback((threadId, content) => {
    setMessages(prev => {
      const msgs = [...(prev[threadId] || [])]
      if (msgs.length === 0) return prev
      msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], content }
      return { ...prev, [threadId]: msgs }
    })
  }, [])

  const renameThread = useCallback((threadId, label) => {
    setThreads(prev =>
      prev.map(t => t.id === threadId ? { ...t, label } : t)
    )
  }, [])

  return (
    <ChatContext.Provider value={{
      threads, activeThread, messages,
      setActive, newThread, addMessage,
      updateLastMessage, renameThread,
      setThreads,
    }}>
      {children}
    </ChatContext.Provider>
  )
}

export const useChat = () => useContext(ChatContext)
