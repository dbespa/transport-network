import styles from './Layout.module.css'
import { Outlet } from 'react-router-dom'

function Layout() {
  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.headerWrapper}>Header</div>
      </header>
      <main className={styles.main}>
        <Outlet />
      </main>
      <footer className={styles.footer}>
        <div className={styles.footerWrapper}>Footer</div>
      </footer>
    </div>
  )
}

export default Layout
