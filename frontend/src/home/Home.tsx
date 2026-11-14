import { Link } from 'react-router-dom'
import { SimulationBadge } from '../components/SimulationBadge'
import './Home.css'

export function Home() {
  return (
    <main className="home">
      <h1>N.A.P.L.E.S.</h1>
      <p>Agenti AI per la resilienza urbana di Napoli</p>
      <SimulationBadge label="Prototipo · scenario simulato" />
      <nav className="home-links">
        <Link to="/control-room">Control room</Link>
        <Link to="/cittadino">Vista cittadino</Link>
      </nav>
    </main>
  )
}
