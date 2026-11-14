import { useState } from 'react'
import { usePiano, type Proposta } from '../api/usePiano'
import { Affidabilita } from '../components/Affidabilita'
import './PianoProposto.css'

// C3: the Orchestrator's plan and the operator's decision. Nothing reaches citizens
// until the operator approves (PROGETTO.md 6.2, step 4).

const AGENTE: Record<string, string> = {
  rischio: 'Rischio',
  mobilita: 'Mobilità',
  folla: 'Folla',
  comunicazione: 'Comunicazione',
}

const CASO: Record<string, string> = {
  A_allarme_ufficiale: 'Caso A · allarme ufficiale',
  B_evento_rilevato: 'Caso B · evento rilevato',
  C_notizia_non_verificata: 'Caso C · non verificata',
}

const STATO: Record<string, string> = {
  proposto: 'Da decidere',
  modificato: 'Modificato, da approvare',
  approvato: 'Approvato',
  rifiutato: 'Rifiutato',
  superato: 'Superato da un piano più recente',
}

type Modo = 'vista' | 'modifica' | 'rifiuto'

const leggibile = (id: string) => id.split('_').join(' ')

export function PianoProposto() {
  const { piano, loaded, approva, modifica, rifiuta } = usePiano()
  const [modo, setModo] = useState<Modo>('vista')
  const [escluse, setEscluse] = useState<string[]>([])
  const [motivo, setMotivo] = useState('')
  const [esito, setEsito] = useState<string | null>(null)
  const [errore, setErrore] = useState<string | null>(null)
  const [occupato, setOccupato] = useState(false)
  const [pianoVisto, setPianoVisto] = useState<string | null>(null)

  // A new plan resets the operator's draft
  if (piano && piano.id !== pianoVisto) {
    setPianoVisto(piano.id)
    setModo('vista')
    setEscluse(piano.proposte_escluse?.map((p) => p.id) ?? [])
    setMotivo('')
    setEsito(null)
    setErrore(null)
  }

  const decidibile = piano?.stato === 'proposto' || piano?.stato === 'modificato'

  const esegui = async (azione: () => Promise<string>) => {
    setOccupato(true)
    setErrore(null)
    try {
      setEsito(await azione())
      setModo('vista')
      setMotivo('')
    } catch (e) {
      setErrore(e instanceof Error ? e.message : 'Operazione non riuscita')
    } finally {
      setOccupato(false)
    }
  }

  const onApprova = () =>
    esegui(async () => {
      const avvisi = await approva(piano!.id)
      return `Piano approvato: ${avvisi.length === 1 ? '1 avviso inviato' : `${avvisi.length} avvisi inviati`} alla vista cittadino.`
    })

  const onModifica = () =>
    esegui(async () => {
      await modifica(piano!.id, escluse, motivo)
      return escluse.length
        ? `Piano modificato: ${escluse.length === 1 ? '1 azione esclusa' : `${escluse.length} azioni escluse`}. Ora va approvato o rifiutato.`
        : 'Piano confermato senza esclusioni. Ora va approvato o rifiutato.'
    })

  const onRifiuta = () =>
    esegui(async () => {
      await rifiuta(piano!.id, motivo)
      return 'Piano rifiutato: nessun avviso inviato. La decisione è nel registro.'
    })

  const alterna = (id: string) =>
    setEscluse((prima) => (prima.includes(id) ? prima.filter((x) => x !== id) : [...prima, id]))

  return (
    <section className="cr-panel cr-panel-plan pp" aria-labelledby="pp-title">
      <div className="pp-head">
        <h2 id="pp-title">Piano proposto</h2>
        {piano && <span className={`badge pp-state pp-state-${piano.stato}`}>{STATO[piano.stato] ?? piano.stato}</span>}
      </div>

      {!loaded ? (
        <p className="cr-todo">In attesa dei dati…</p>
      ) : !piano ? (
        <p className="cr-todo">Nessun piano: a questo minuto gli agenti non hanno proposte.</p>
      ) : (
        <>
          <p className="pp-meta">
            {leggibile(piano.id)} · minuto {piano.t_min}
            {piano.affidabilita_minima && (
              <>
                {' · affidabilità minima '}
                <Affidabilita value={piano.affidabilita_minima} />
              </>
            )}
          </p>
          {piano.sintesi_modello ? (
            <div className="pp-summary-model">
              <span className="badge badge-reliable">Spiegazione scritta da Claude · controllata sugli stessi dati</span>
              <p className="pp-summary">{piano.sintesi_modello}</p>
              <details className="pp-summary-rules">
                <summary>Sintesi a regole</summary>
                <p>{piano.sintesi}</p>
              </details>
            </div>
          ) : (
            <p className="pp-summary">{piano.sintesi}</p>
          )}

          <ol className="pp-list">
            {[...piano.proposte]
              .sort((a, b) => b.priorita - a.priorita)
              .map((p) => (
                <PropostaRiga
                  key={p.id}
                  p={p}
                  modo={modo}
                  esclusa={escluse.includes(p.id)}
                  onToggle={() => alterna(p.id)}
                />
              ))}
          </ol>

          {piano.proposte_escluse && piano.proposte_escluse.length > 0 && modo === 'vista' && (
            <div className="pp-excluded">
              <strong>Escluse dall'operatore</strong>
              <ul>
                {piano.proposte_escluse.map((p) => (
                  <li key={p.id}>{p.titolo}</li>
                ))}
              </ul>
              {piano.motivo_modifica && <p>Motivo: {piano.motivo_modifica}</p>}
            </div>
          )}

          {piano.conflitti && piano.conflitti.length > 0 && (
            <div className="pp-block">
              <h3>Conflitti risolti dall'Orchestratore</h3>
              <ul>
                {piano.conflitti.map((c) => (
                  <li key={c.risorsa}>{c.risoluzione}</li>
                ))}
              </ul>
            </div>
          )}

          {piano.impatto && piano.impatto.zone.length > 0 && (
            <div className="pp-block">
              <h3>
                Impatto stimato{' '}
                {piano.impatto.stub ? (
                  <span className="badge badge-unconfirmed">stima provvisoria</span>
                ) : (
                  <span className="badge badge-simulated">simulatore</span>
                )}
              </h3>
              <table className="pp-impact">
                <thead>
                  <tr>
                    <th scope="col">Zona</th>
                    <th scope="col">Deflusso con / senza</th>
                    <th scope="col">Picco con / senza</th>
                  </tr>
                </thead>
                <tbody>
                  {piano.impatto.zone
                    .filter((z) => z.deflusso_min_senza_piano > 0 || z.picco_carico_senza_piano > 0)
                    .map((z) => (
                      <tr key={z.zona}>
                        <th scope="row">{leggibile(z.zona)}</th>
                        <td>
                          {z.deflusso_min_con_piano} / {z.deflusso_min_senza_piano} min
                        </td>
                        <td>
                          {z.picco_carico_con_piano.toFixed(1)} / {z.picco_carico_senza_piano.toFixed(1)}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
              <p className="pp-note">Picco: persone rispetto alla capienza della zona (1,0 = piena).</p>
            </div>
          )}

          {decidibile && (
            <div className="pp-actions">
              {modo === 'vista' && (
                <>
                  <button className="btn-primary" onClick={onApprova} disabled={occupato}>
                    Approva
                  </button>
                  <button className="btn-secondary" onClick={() => setModo('modifica')} disabled={occupato}>
                    Modifica
                  </button>
                  <button className="btn-danger" onClick={() => setModo('rifiuto')} disabled={occupato}>
                    Rifiuta
                  </button>
                </>
              )}

              {modo === 'modifica' && (
                <div className="pp-form">
                  <p>Seleziona le azioni da escludere. Le allerte ufficiali (caso A) non si possono escludere.</p>
                  <label>
                    Motivo (facoltativo)
                    <input value={motivo} onChange={(e) => setMotivo(e.target.value)} />
                  </label>
                  <div className="pp-form-buttons">
                    <button className="btn-primary" onClick={onModifica} disabled={occupato}>
                      Conferma modifica
                    </button>
                    <button className="btn-ghost" onClick={() => setModo('vista')} disabled={occupato}>
                      Annulla
                    </button>
                  </div>
                </div>
              )}

              {modo === 'rifiuto' && (
                <div className="pp-form">
                  <label>
                    Motivo del rifiuto
                    <input value={motivo} onChange={(e) => setMotivo(e.target.value)} required />
                  </label>
                  <div className="pp-form-buttons">
                    <button className="btn-danger" onClick={onRifiuta} disabled={occupato || !motivo.trim()}>
                      Conferma rifiuto
                    </button>
                    <button className="btn-ghost" onClick={() => setModo('vista')} disabled={occupato}>
                      Annulla
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {esito && (
            <p className="pp-result" role="status">
              {esito}
            </p>
          )}
          {errore && (
            <p className="pp-error" role="alert">
              {errore}
            </p>
          )}
        </>
      )}
    </section>
  )
}

function PropostaRiga({
  p,
  modo,
  esclusa,
  onToggle,
}: {
  p: Proposta
  modo: Modo
  esclusa: boolean
  onToggle: () => void
}) {
  const ufficiale = p.caso === 'A_allarme_ufficiale'
  return (
    <li className={`pp-item${esclusa ? ' is-excluded' : ''}`}>
      {modo === 'modifica' && (
        <input
          type="checkbox"
          className="pp-check"
          aria-label={`Escludi: ${p.titolo}`}
          checked={esclusa}
          disabled={ufficiale}
          onChange={onToggle}
        />
      )}
      <div className="pp-item-body">
        <div className="pp-item-tags">
          <span className="pp-agent">{AGENTE[p.agente] ?? p.agente}</span>
          <span className="pp-priority" title="5 = sicurezza delle persone">
            priorità {p.priorita}
          </span>
          <Affidabilita value={p.affidabilita} />
          {p.caso && <span className="badge badge-reliable">{CASO[p.caso] ?? p.caso}</span>}
        </div>
        <strong className="pp-item-title">{p.titolo}</strong>
        <p className="pp-item-why">{p.motivazione}</p>
      </div>
    </li>
  )
}
