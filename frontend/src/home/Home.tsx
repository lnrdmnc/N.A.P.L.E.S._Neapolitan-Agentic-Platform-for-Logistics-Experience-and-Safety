import { Link } from 'react-router-dom'
import { SimulationBadge } from '../components/SimulationBadge'
import './Home.css'

const VISTE = [
  {
    to: '/control-room',
    titolo: 'Control room',
    per: 'Per l’operatore del Comune · schermo grande',
    testo:
      'Gli agenti si coordinano sotto i tuoi occhi: messaggi, piano con il grado di certezza dei dati, Approva, Modifica o Rifiuta, indicatori con e senza coordinamento, traffico reale.',
  },
  {
    to: '/cittadino',
    titolo: 'Vista cittadino',
    per: 'Per chi è in città · sul telefono',
    testo:
      'Solo gli avvisi che ti riguardano, per tifoso, residente, pendolare o turista in inglese, sempre con la fonte. Si installa sulla home come un’app.',
  },
]

const PASSI = [
  'Apri la control room sul computer e la vista cittadino sul telefono.',
  'Nella control room avvia lo scenario: alle 21:55 arriva lo sciame sismico simulato e gli agenti propongono un piano.',
  'Approva il piano: l’avviso arriva sul telefono in pochi secondi.',
]

export function Home() {
  return (
    <div className="home">
      <div className="home-bg" aria-hidden="true">
        <div className="home-bg-img home-bg-tramonto" />
        <div className="home-bg-img home-bg-notte" />
        <div className="home-bg-velo" />
      </div>

      <main className="home-main">
        <header className="home-hero">
          <img
            className="home-logo"
            src="/img/logo-naples-coscienze.png"
            alt="N.A.P.L.E.S. · Team CoScienze · The Big Hack 2026"
          />
          <h1>N.A.P.L.E.S.</h1>
          <p className="home-sigla">Neapolitan Agentic Platform for Logistics, Experience and Safety</p>
          <p className="home-claim">
            Agenti AI che si coordinano per la resilienza urbana di Napoli. L’operatore decide, il cittadino
            sa cosa fare, ogni passo resta in un registro verificabile.
          </p>
          <SimulationBadge label="Prototipo · eventi di emergenza simulati, traffico e contesto reali" />
        </header>

        <nav className="home-viste" aria-label="Le due viste">
          {VISTE.map((v) => (
            <Link key={v.to} to={v.to} className="home-vista">
              <span className="home-vista-per">{v.per}</span>
              <span className="home-vista-titolo">
                {v.titolo} <span aria-hidden="true">→</span>
              </span>
              <span className="home-vista-testo">{v.testo}</span>
            </Link>
          ))}
        </nav>

        <section className="home-passi" aria-labelledby="home-passi-titolo">
          <h2 id="home-passi-titolo">Provala in un minuto</h2>
          <ol>
            {PASSI.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ol>
        </section>

        <footer className="home-footer">
          N.A.P.L.E.S. affianca INGV e Protezione Civile, non li sostituisce: gli allarmi ufficiali
          arrivano da IT-Alert. Team CoScienze · The Big Hack 2026 · «Napoli Agentic City».
        </footer>
      </main>
    </div>
  )
}
