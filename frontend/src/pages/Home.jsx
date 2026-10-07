// frontend/src/pages/Home.jsx
import { useChat } from '../context/ChatContext'
import styles from './Home.module.css'

const CARDS = [
  {
    id:    'chat',
    icon:  '◎',
    title: 'Chatbot',
    desc:  'Conversational AI with full memory across sessions.',
    tag:   'LangGraph + Groq',
    color: 'purple',
  },
  {
    id:    'rag',
    icon:  '⊞',
    title: 'RAG',
    desc:  'Upload documents and ask questions grounded in your data.',
    tag:   'Pinecone + LLaMA',
    color: 'teal',
  },
  {
    id:    'research',
    icon:  '⊹',
    title: 'Research Agent',
    desc:  'AI searches the web and synthesises a detailed answer.',
    tag:   'Tavily + Groq',
    color: 'coral',
  },
  {
    id:    'research',
    icon:  '◈',
    title: 'Critic',
    desc:  'Scores and reviews the research output for quality.',
    tag:   'Self-critique loop',
    color: 'amber',
  },
]

export default function Home({ onNavigate }) {
  const { newThread } = useChat()

  const handleCard = (id) => {
    if (id === 'chat') newThread()
    onNavigate(id)
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.badge}>◆ NexusAI</div>
        <h1 className={styles.title}>Your AI Intelligence Layer</h1>
        <p className={styles.subtitle}>Four powerful tools. One unified interface.</p>
      </div>

      <div className={styles.grid}>
        {CARDS.map((card, i) => (
          <button
            key={i}
            className={`${styles.card} ${styles[card.color]}`}
            onClick={() => handleCard(card.id)}
          >
            <span className={styles.cardIcon}>{card.icon}</span>
            <div className={styles.cardContent}>
              <h2 className={styles.cardTitle}>{card.title}</h2>
              <p className={styles.cardDesc}>{card.desc}</p>
            </div>
            <span className={styles.cardTag}>{card.tag}</span>
            <span className={styles.cardArrow}>→</span>
          </button>
        ))}
      </div>

      <div className={styles.stack}>
        {['Groq · LLaMA 3.1', 'LangGraph', 'Pinecone', 'SQLite'].map((s, i) => (
          <span key={i} className={styles.stackItem}>{s}</span>
        ))}
      </div>
    </div>
  )
}
