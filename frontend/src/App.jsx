// frontend/src/App.jsx
import { useState } from 'react'
import { ChatProvider } from './context/ChatContext'
import Sidebar from './components/Sidebar'
import Home from './pages/Home'
import Chat from './pages/Chat'
import RAG from './pages/RAG'
import Research from './pages/Research'
import styles from './App.module.css'

export default function App() {
  const [page, setPage] = useState('home')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navigate = (p) => {
    setPage(p)
    setSidebarOpen(false)
  }

  const renderPage = () => {
    switch (page) {
      case 'home':     return <Home onNavigate={navigate} />
      case 'chat':     return <Chat />
      case 'rag':      return <RAG />
      case 'research': return <Research />
      default:         return <Home onNavigate={navigate} />
    }
  }

  return (
    <ChatProvider>
      <div className={styles.layout}>
        {/* Mobile top-bar */}
        <header className={styles.mobileTopBar}>
          <button
            className={styles.hamburger}
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
          >
            <span /><span /><span />
          </button>
          <span className={styles.mobileLogoText}>NexusAI</span>
          <span className={styles.mobileLogoIcon}>◆</span>
        </header>

        {/* Backdrop */}
        {sidebarOpen && (
          <div
            className={styles.backdrop}
            onClick={() => setSidebarOpen(false)}
          />
        )}

        <Sidebar
          page={page}
          onNavigate={navigate}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        <main className={styles.main}>
          {renderPage()}
        </main>
      </div>
    </ChatProvider>
  )
}
