// frontend/src/components/Sidebar.jsx
import { useChat } from '../context/ChatContext'
import styles from './Sidebar.module.css'

export default function Sidebar({ page, onNavigate, isOpen, onClose }) {
  const { threads, activeThread, setActive, newThread } = useChat()

  const handleNew = () => {
    newThread()
    onNavigate('chat')
  }

  return (
    <aside className={`${styles.sidebar} ${isOpen ? styles.sidebarOpen : ''}`}>
      {/* Mobile close button */}
      <button className={styles.closeBtn} onClick={onClose} aria-label="Close menu">✕</button>

      {/* Logo */}
      <div className={styles.logo}>
        <span className={styles.logoIcon}>◆</span>
        <span className={styles.logoText}>NexusAI</span>
      </div>

      {/* New chat button */}
      <button className={styles.newChat} onClick={handleNew}>
        <span>+</span> New chat
      </button>

      {/* Nav */}
      <nav className={styles.nav}>
        <button
          className={`${styles.navItem} ${page === 'home' ? styles.active : ''}`}
          onClick={() => onNavigate('home')}
        >
          <span className={styles.navIcon}>⌂</span> Home
        </button>
        <button
          className={`${styles.navItem} ${page === 'chat' ? styles.active : ''}`}
          onClick={() => onNavigate('chat')}
        >
          <span className={styles.navIcon}>◎</span> Chat
        </button>
        <button
          className={`${styles.navItem} ${page === 'rag' ? styles.active : ''}`}
          onClick={() => onNavigate('rag')}
        >
          <span className={styles.navIcon}>⊞</span> Documents
        </button>
        <button
          className={`${styles.navItem} ${page === 'research' ? styles.active : ''}`}
          onClick={() => onNavigate('research')}
        >
          <span className={styles.navIcon}>⊹</span> Research
        </button>
      </nav>

      {/* Thread history */}
      {threads.length > 0 && (
        <div className={styles.history}>
          <p className={styles.historyLabel}>Recent</p>
          {threads.slice(0, 20).map(t => (
            <button
              key={t.id}
              className={`${styles.thread} ${activeThread === t.id ? styles.threadActive : ''}`}
              onClick={() => { setActive(t.id); onNavigate('chat') }}
            >
              <span className={styles.threadDot} />
              <span className={styles.threadLabel}>{t.label}</span>
            </button>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className={styles.footer}>
        <div className={styles.footerAvatar}>N</div>
        <span className={styles.footerName}>Nitesh</span>
      </div>
    </aside>
  )
}
