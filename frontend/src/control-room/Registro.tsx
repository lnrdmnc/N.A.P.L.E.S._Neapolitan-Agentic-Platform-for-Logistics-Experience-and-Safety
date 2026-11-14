import { type VoceRegistro, useRegistro } from '../api/useRegistro'
import './Registro.css'

// C4 · Decision log: every event, plan, decision and alert, chained by hashes.
// Each entry carries the hash of the previous one: changing any past entry breaks the chain,
// and the server's check says where (also from a terminal: make verifica-registro).

const TIPI: Record<string, string> = {
  evento: 'Evento',
  piano_proposto: 'Piano proposto',
  piano_approvato: 'Approvato',
  piano_modificato: 'Modificato',
  piano_rifiutato: 'Rifiutato',
  avviso_inviato: 'Avviso inviato',
}

const MAX_VISIBILI = 30

function descrivi(v: VoceRegistro): string {
  const c = v.contenuto as Record<string, unknown>
  switch (v.tipo) {
    case 'evento':
      return String(c.titolo ?? c.id ?? '')
    case 'piano_proposto':
      return `${c.piano}: ${Array.isArray(c.azioni) ? c.azioni.length : 0} azioni`
    case 'piano_approvato':
      return `${c.piano} · da ${c.operatore}`
    case 'piano_modificato':
      return `${c.piano} · escluse: ${Array.isArray(c.escluse) && c.escluse.length ? c.escluse.join(', ') : 'nessuna'}`
    case 'piano_rifiutato':
      return `${c.piano} · da ${c.operatore}${c.motivo ? ` · ${c.motivo}` : ''}`
    case 'avviso_inviato':
      return `${c.pubblico}${c.ufficiale ? ' · ufficiale' : ''} · ${c.headline}`
    default:
      return JSON.stringify(c)
  }
}

const breve = (hash: string) => `${hash.slice(0, 8)}…`

export function Registro() {
  const { registro, error, verificatoAlle, verifica } = useRegistro()
  const voci = registro ? registro.voci.slice(-MAX_VISIBILI).reverse() : []
  const alterata = registro?.prima_voce_alterata

  return (
    <section className="cr-panel cr-panel-log" aria-labelledby="reg-title">
      <div className="cr-log-head">
        <h2 id="reg-title">Registro delle decisioni</h2>
        <button type="button" className="reg-button" onClick={() => void verifica()}>
          Verifica la catena
        </button>
      </div>

      {error && <p className="cr-error">{error}</p>}

      {registro && (
        <div className={`reg-status ${registro.integro ? 'is-ok' : 'is-broken'}`} role="status">
          <strong>
            {registro.integro
              ? `Catena integra · ${registro.voci.length} voci`
              : `Catena ALTERATA dalla voce ${alterata}`}
          </strong>
          <span>
            {registro.integro
              ? 'Ogni voce contiene l’impronta (hash) della precedente: nessuna è stata cambiata, tolta o spostata.'
              : 'Una voce passata non corrisponde più alla catena: il registro è stato manomesso.'}
            {verificatoAlle && ` Verificata alle ${verificatoAlle.toLocaleTimeString('it-IT')}.`}
          </span>
        </div>
      )}

      {registro && registro.voci.length === 0 && <p className="cr-todo">Nessuna voce fino a questo minuto.</p>}

      <ol className="reg-list">
        {voci.map((v) => (
          <li key={v.indice} className={`reg-item reg-${v.tipo}${alterata === v.indice ? ' is-broken' : ''}`}>
            <span className="reg-index">#{v.indice}</span>
            <span className="reg-time">min {v.t_min}</span>
            <span className="reg-kind">{TIPI[v.tipo] ?? v.tipo}</span>
            <span className="reg-text">{descrivi(v)}</span>
            <code className="reg-hash" title={`hash ${v.hash}\nprecedente ${v.hash_precedente}`}>
              {breve(v.hash_precedente)} → {breve(v.hash)}
            </code>
          </li>
        ))}
      </ol>
      <p className="reg-foot">Anche da terminale, sul file scritto dalla demo: <code>make verifica-registro</code></p>
    </section>
  )
}
