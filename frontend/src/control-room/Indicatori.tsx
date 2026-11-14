import { type Indicatori as Dati, useIndicatori } from '../api/useIndicatori'
import { SimulationBadge } from '../components/SimulationBadge'
import './Indicatori.css'

// C5 · Same indicators, same scenario, same zone simulator as the map: with and without
// coordination. Every number shows where it comes from (PIANO.md, section 9).

type Origine = 'calcolato' | 'misurato_in_sessione' | 'ipotesi'

const ORIGINI: Record<Origine, { label: string; className: string }> = {
  calcolato: { label: 'calcolato', className: 'badge-reliable' },
  misurato_in_sessione: { label: 'misurato in sessione', className: 'kpi-badge-measured' },
  ipotesi: { label: 'ipotesi', className: 'badge-unconfirmed' },
}

const ZONE: Record<string, string> = {
  piazzale_tecchio: 'Piazzale Tecchio',
  viale_giochi_del_mediterraneo: 'Viale Giochi del Mediterraneo',
  stazione_campi_flegrei: 'Stazione Campi Flegrei (L2)',
  stazione_mostra: 'Stazione Mostra (Cumana)',
  fermata_marino_stadio: 'Fermata Marino - Stadio',
}

const numero = new Intl.NumberFormat('it-IT')

function OrigineBadge({ value }: { value?: string }) {
  const o = ORIGINI[(value ?? 'ipotesi') as Origine] ?? ORIGINI.ipotesi
  return <span className={`badge ${o.className}`}>{o.label}</span>
}

type Riga = {
  chiave: string
  etichetta: string
  unita: string
  valore: (i: Dati) => number
  nota?: string
}

const RIGHE: Riga[] = [
  {
    chiave: 'picco_attesa_persone',
    etichetta: 'Picco di persone in attesa fuori dallo stadio',
    unita: 'persone',
    valore: (i) => i.picco_attesa_persone,
  },
  {
    chiave: 'deflusso_min',
    etichetta: "Area dello stadio sgombra dopo il fischio finale",
    unita: 'min',
    valore: (i) => i.deflusso_min,
    nota: "Il vantaggio sullo sgombero dipende dall'ipotesi sui percorsi a piedi (docs/IPOTESI.md).",
  },
  {
    chiave: 'minuti_evento_avviso',
    etichetta: "Dall'evento al primo avviso",
    unita: 'min',
    valore: (i) => i.minuti_evento_avviso,
  },
  {
    chiave: 'minuti_decisione',
    etichetta: "Dall'evento alla decisione",
    unita: 'min',
    valore: (i) => i.minuti_decisione,
  },
]

function differenza(senza: number, con: number, unita: string) {
  if (senza === con) return 'uguale'
  if (unita === 'persone' && senza > 0) {
    const perc = Math.round(((con - senza) / senza) * 100)
    return `${perc > 0 ? '+' : ''}${perc}%`
  }
  const d = con - senza
  return `${d > 0 ? '+' : ''}${d} ${unita}`
}

export function Indicatori() {
  const { dati, error } = useIndicatori()
  const con = dati?.con_coordinamento
  const senza = dati?.senza_coordinamento
  const zone = con ? Object.keys(con.congestione_zone ?? {}) : []
  const massimo = Math.max(
    1.5,
    ...zone.map((z) => Math.max(con?.congestione_zone?.[z] ?? 0, senza?.congestione_zone?.[z] ?? 0)),
  )

  return (
    <section className="cr-panel cr-panel-kpi" aria-labelledby="kpi-title">
      <div className="kpi-head">
        <h2 id="kpi-title">Con e senza coordinamento</h2>
        <SimulationBadge label="scenario simulato" />
      </div>
      <p className="kpi-lead">
        Stesso scenario, stesso simulatore della mappa. Il risultato che regge con ogni ipotesi:{' '}
        <strong>meno affollamento e nessuna folla davanti alle stazioni chiuse.</strong>
      </p>

      {error && <p className="cr-error">{error}</p>}
      {!dati && !error && <p className="cr-todo">In attesa dei dati…</p>}

      {con && senza && (
        <>
          <table className="kpi-table">
            <thead>
              <tr>
                <th scope="col">Indicatore</th>
                <th scope="col">Senza</th>
                <th scope="col">Con</th>
                <th scope="col">Differenza</th>
              </tr>
            </thead>
            <tbody>
              {RIGHE.map((r) => {
                const vs = r.valore(senza)
                const vc = r.valore(con)
                return (
                  <tr key={r.chiave}>
                    <th scope="row">
                      {r.etichetta}
                      {r.nota && <span className="kpi-note">{r.nota}</span>}
                    </th>
                    <td data-label="Senza">
                      <span className="kpi-value">
                        {numero.format(vs)} <small>{r.unita}</small>
                      </span>
                      <OrigineBadge value={senza.origine?.[r.chiave]} />
                    </td>
                    <td data-label="Con">
                      <span className="kpi-value kpi-value-con">
                        {numero.format(vc)} <small>{r.unita}</small>
                      </span>
                      <OrigineBadge value={con.origine?.[r.chiave]} />
                    </td>
                    <td data-label="Differenza" className={vc < vs ? 'kpi-better' : vc > vs ? 'kpi-worse' : ''}>
                      {differenza(vs, vc, r.unita)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>

          <div className="kpi-zones">
            <h3>
              Affollamento massimo per zona <small>(1 = zona piena)</small>{' '}
              <OrigineBadge value={con.origine?.congestione_zone} />
            </h3>
            <ul>
              {zone.map((z) => {
                const s = senza.congestione_zone?.[z] ?? 0
                const c = con.congestione_zone?.[z] ?? 0
                return (
                  <li key={z}>
                    <span className="kpi-zone-name">{ZONE[z] ?? z}</span>
                    <div className="kpi-bars" aria-label={`senza ${s}, con ${c}`}>
                      <span className="kpi-full" style={{ left: `${(1 / massimo) * 100}%` }} aria-hidden="true" />
                      <span className="kpi-bar kpi-bar-senza" style={{ width: `${(s / massimo) * 100}%` }}>
                        <em>senza {s.toLocaleString('it-IT')}</em>
                      </span>
                      <span className="kpi-bar kpi-bar-con" style={{ width: `${(c / massimo) * 100}%` }}>
                        <em>con {c.toLocaleString('it-IT')}</em>
                      </span>
                    </div>
                  </li>
                )
              })}
            </ul>
          </div>

          <details className="kpi-ipotesi">
            <summary>Ipotesi usate ({dati?.ipotesi.length})</summary>
            <ul>
              {dati?.ipotesi.map((i) => (
                <li key={i}>{i}</li>
              ))}
            </ul>
          </details>
        </>
      )}
    </section>
  )
}
