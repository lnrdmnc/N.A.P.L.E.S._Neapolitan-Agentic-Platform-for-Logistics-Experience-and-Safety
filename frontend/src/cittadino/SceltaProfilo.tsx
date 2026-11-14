import { PROFILI, type Profilo } from '../api/profilo'
import './SceltaProfilo.css'

// U1 · The citizen says who they are; alerts follow. Bilingual so a tourist can choose too.
export function SceltaProfilo({
  profilo,
  onScegli,
}: {
  profilo: Profilo | null
  onScegli: (p: Profilo | null) => void
}) {
  const scelto = PROFILI.find((p) => p.id === profilo)

  if (scelto) {
    const en = scelto.lingua === 'en'
    return (
      <div className="pf-current">
        <span>
          {en ? 'Alerts for' : 'Avvisi per'}: <strong>{scelto.titolo}</strong>
        </span>
        <button type="button" onClick={() => onScegli(null)}>
          {en ? 'Change' : 'Cambia'}
        </button>
      </div>
    )
  }

  return (
    <section className="pf" aria-labelledby="pf-title">
      <h2 id="pf-title">
        Chi sei? <span lang="en">Who are you?</span>
      </h2>
      <p className="pf-note">
        Ricevi solo gli avvisi che ti riguardano. Nessun dato personale: la scelta resta sul telefono.
      </p>
      <div className="pf-options">
        {PROFILI.map((p) => (
          <button key={p.id} type="button" lang={p.lingua} onClick={() => onScegli(p.id)}>
            <strong>{p.titolo}</strong>
            <span>{p.sottotitolo}</span>
          </button>
        ))}
      </div>
    </section>
  )
}
