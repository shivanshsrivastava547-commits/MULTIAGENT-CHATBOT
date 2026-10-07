import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import styles from './MessageBubble.module.css'

export default function MessageBubble({ role, content, isStreaming }) {
  const isUser = role === 'user'

  return (
    <div className={`${styles.row} ${isUser ? styles.userRow : styles.aiRow}`}>
      {!isUser && <div className={styles.avatar}>◆</div>}
      <div className={`${styles.bubble} ${isUser ? styles.userBubble : styles.aiBubble}`}>
        {isUser ? (
          <p>{content}</p>
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, className, children, ...props }) {
                const isBlock = node?.position?.start?.line !== node?.position?.end?.line
                  || String(children).includes('\n')
                return isBlock ? (
                  <pre className={styles.codeBlock}>
                    <code className={className} {...props}>{children}</code>
                  </pre>
                ) : (
                  <code className={styles.inlineCode} {...props}>{children}</code>
                )
              },
              p({ children }) { return <p className={styles.para}>{children}</p> },
              ul({ children }) { return <ul className={styles.ul}>{children}</ul> },
              ol({ children }) { return <ol className={styles.ol}>{children}</ol> },
              li({ children }) { return <li className={styles.li}>{children}</li> },
              strong({ children }) { return <strong className={styles.strong}>{children}</strong> },
              h1({ children }) { return <h1 className={styles.h1}>{children}</h1> },
              h2({ children }) { return <h2 className={styles.h2}>{children}</h2> },
              h3({ children }) { return <h3 className={styles.h3}>{children}</h3> },
            }}
          >
            {content || ''}
          </ReactMarkdown>
        )}
        {isStreaming && <span className={styles.cursor} />}
      </div>
      {isUser && <div className={`${styles.avatar} ${styles.userAvatar}`}>N</div>}
    </div>
  )
}