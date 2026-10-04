import styles from './Home.module.css'
import 'leaflet/dist/leaflet.css'
import MapComponent from '../../components/MapComponent/MapComponent'

function Home() {
  return (
    <div className={styles.wrapper}>
      <MapComponent />
    </div>
  )
}

export default Home
