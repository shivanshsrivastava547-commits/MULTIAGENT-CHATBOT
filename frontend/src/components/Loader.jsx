// frontend/src/components/Loader.jsx
import styles from './Loader.module.css'

export default function Loader({ size = 'md' }) {
  return <div className={`${styles.loader} ${styles[size]}`} />
}
