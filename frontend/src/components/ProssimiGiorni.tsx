import { type EventoPrevisto, type ScioperoPrevisto, useProssimiGiorni } from '../api/useProssimiGiorni'
import './ProssimiGiorni.css'

// «Napoli oggi e nei prossimi giorni»: what is coming, which area it hits and when, what to use
// instead. Used by the citizen view (card) and the control room (panel).

const TIPI: Record<string, string> = {
  partita: 'Partita',
  concerto: 'Concerto',
  manifestazione: 'Manifestazione',
  altro: 'Evento',
}

const LIVELLI: Record<string, string> = { alto: 'Affollamento alto', medio: 'Affollamento medio', basso: 'Affollamento basso' }

const numero = new Intl.NumberFormat('it-IT')

function Evento({ p }: { p: EventoPrevisto }) {
  const { evento: e, impatto: i } = p
  const ora = e.inizio.slice(11, 16)
  return (
    <article className={`pg-evento pg-${i.livello}`}>
      <div className="pg-head">
        <span className="pg-when">
          <strong>{p.giorno}</strong> {ora}
        </span>
        <span className="pg-kind">{TIPI[e.tipo] ?? e.tipo}</span>
      </div>
      <h3>{e.titolo}</h3>
      <p className="pg-where">
        {e.luogo} · {e.quartiere}
        {e.persone_attese
          ? ` · circa ${numero.format(e.persone_attese)} persone${e.affidabilita === 'ufficiale' ? '' : ' (stima)'}`
          : ''}
      </p>
      <div className="pg-tags">
        <span className={`badge pg-level-${i.livello}`}>{LIVELLI[i.livello]}</span>
        {e.esempio ? (
          <span className="badge badge-unconfirmed">Esempio, da verificare</span>
        ) : e.affidabilita === 'ufficiale' ? (
          <span className="badge badge-reliable">Dato reale · {e.fonte}</span>
        ) : e.affidabilita === 'stimata' ? (
          <span className="badge badge-reliable">In programma · {e.fonte}</span>
        ) : (
          <span className="badge badge-unconfirmed">Da verificare</span>
        )}
      </div>
      <dl className="pg-impact">
        <div>
          <dt>Zona interessata</dt>
          <dd>{i.zona}</dd>
        </div>
        <div>
          <dt>Quando è affollata</dt>
          <dd>{i.finestre.map((f) => `${f.da}–${f.a} ${f.motivo}`).join(', ')}</dd>
        </div>
        <div>
          <dt>Da evitare</dt>
          <dd>{i.da_evitare.join(', ')}</dd>
        </div>
        <div className="pg-alt">
          <dt>Usa invece</dt>
          <dd>{i.alternative.join(', ')}</dd>
        </div>
      </dl>
      {e.esempio && <p className="pg-source">Fonte: {e.fonte}</p>}
    </article>
  )
}

const quando = (iso: string) =>
  new Date(iso).toLocaleString('it-IT', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Europe/Rome',
  })

function Sciopero({ p }: { p: ScioperoPrevisto }) {
  const s = p.sciopero
  return (
    <article className="pg-evento pg-sciopero">
      <div className="pg-head">
        <span className="pg-when">
          <strong>{p.giorno}</strong> {s.settore}
        </span>
        <span className="pg-kind">{s.rilevanza === 'Nazionale' ? 'Sciopero nazionale' : 'Sciopero'}</span>
      </div>
      <h3 className="pg-capital">{p.linee_coinvolte.join(', ')}</h3>
      <p className="pg-where">
        Da {quando(s.inizio)} a {quando(s.fine)} · {s.categoria.toLowerCase()}
      </p>
      <div className="pg-tags">
        <span className="badge badge-reliable">Dato ufficiale · Ministero dei Trasporti</span>
      </div>
      <dl className="pg-impact">
        <div>
          <dt>Orario pubblicato</dt>
          <dd>{s.orario}</dd>
        </div>
        {p.eventi_coinvolti.length > 0 && (
          <div className="pg-warn">
            <dt>Attenzione</dt>
            <dd>{p.eventi_coinvolti.join('; ')}</dd>
          </div>
        )}
        {p.linee_non_coinvolte.length > 0 && (
          <div className="pg-alt">
            <dt>Non coinvolte</dt>
            <dd>{p.linee_non_coinvolte.join(', ')}</dd>
          </div>
        )}
      </dl>
      <p className="pg-source">Fasce garantite e adesioni: verifica sul sito dell'azienda.</p>
    </article>
  )
}

export function ProssimiGiorni({ variante }: { variante: 'cittadino' | 'control-room' }) {
  const { dati, error } = useProssimiGiorni()
  const classe = variante === 'cittadino' ? 'ct-card pg pg-cittadino' : 'pg pg-cr'

  return (
    <section className={classe} aria-labelledby={`pg-title-${variante}`}>
      <h2 id={`pg-title-${variante}`}>Napoli oggi e nei prossimi giorni</h2>
      <p className="pg-lead">
        Eventi in arrivo, zone che si affollano e come muoversi prima che succeda.
      </p>
      {error && <p className="cr-error">{error}</p>}
      {dati && dati.eventi.length === 0 && <p className="pg-lead">Nessun grande evento previsto.</p>}
      <div className="pg-list">
        {dati?.eventi.map((p) => (
          <Evento key={p.evento.id} p={p} />
        ))}
      </div>
      {dati && dati.scioperi && dati.scioperi.length > 0 && (
        <>
          <h3 className="pg-subtitle">Scioperi dei trasporti</h3>
          <div className="pg-list">
            {dati.scioperi.map((p) => (
              <Sciopero key={p.sciopero.id} p={p} />
            ))}
          </div>
        </>
      )}
      {dati && (
        <p className="pg-source">
          Fonti:{' '}
          {dati.fonti
            .map((f) => `${f.nome}${f.disponibile ? '' : ' (non disponibile)'}${f.copia ? ' (copia salvata)' : ''}`)
            .join(' · ')}
        </p>
      )}
    </section>
  )
}
