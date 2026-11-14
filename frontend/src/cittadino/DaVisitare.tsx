import { useState } from 'react'
import { type LuogoConsigliato, useDaVisitare } from '../api/useDaVisitare'
import './DaVisitare.css'

// «Cosa visitare»: real places (OpenStreetMap), nearest metro and funicular stops (ANM GTFS), and
// advice that changes with real events and official strikes. In English for the tourist profile.

const STATI = {
  consigliato: { it: 'Consigliato', en: 'Recommended' },
  con_disagi: { it: 'Con disagi', en: 'Disruptions' },
  da_evitare_ora: { it: 'Da evitare ora', en: 'Avoid now' },
} as const

const VISIBILI = 6

function Luogo({ l, en }: { l: LuogoConsigliato; en: boolean }) {
  const motivi = en ? l.motivi_en : l.motivi
  return (
    <li className={`dv-luogo dv-${l.stato}`}>
      <div className="dv-head">
        <strong>{en ? l.name_en : l.nome}</strong>
        <span className={`badge dv-badge-${l.stato}`}>{STATI[l.stato][en ? 'en' : 'it']}</span>
      </div>
      <p className="dv-descr">
        {l.zona} · {en ? l.description_en : l.descrizione}
      </p>
      {motivi && motivi.length > 0 && <p className="dv-motivo">{motivi.join('; ')}</p>}
      <ul className="dv-accessi">
        {l.accessi.map((a) => (
          <li key={a.codice} className={a.disponibile ? '' : 'is-off'}>
            <span className="dv-linea">{a.linea}</span> {a.fermata} ·{' '}
            {en ? `${a.minuti_a_piedi} min walk` : `${a.minuti_a_piedi} min a piedi`}
            {!a.disponibile && <em> · {en ? a.motivo_en : a.motivo}</em>}
          </li>
        ))}
      </ul>
    </li>
  )
}

export function DaVisitare({ en = false }: { en?: boolean }) {
  const [quando, setQuando] = useState<string | null>(null)
  const [tutti, setTutti] = useState(false)
  const { dati, error } = useDaVisitare(quando)
  const luoghi = dati ? (tutti ? dati.luoghi : dati.luoghi.slice(0, VISIBILI)) : []

  return (
    <section className="ct-card dv" aria-labelledby="dv-title">
      <h2 id="dv-title">{en ? 'What to visit' : 'Cosa visitare'}</h2>
      <p className="ct-muted">
        {en
          ? 'Real places and how to get there, considering events and official strikes.'
          : 'Luoghi veri e come arrivarci, tenendo conto di eventi e scioperi ufficiali.'}
      </p>
      {dati && dati.momenti.length > 1 && (
        <label className="dv-quando">
          {en ? 'When' : 'Quando'}
          <select value={quando ?? ''} onChange={(e) => setQuando(e.target.value || null)}>
            {dati.momenti.map((m, i) => (
              <option key={m.quando} value={i === 0 ? '' : m.quando}>
                {en ? m.label_en : m.etichetta}
              </option>
            ))}
          </select>
        </label>
      )}
      {error && <p className="cr-error">{error}</p>}
      <ul className="dv-lista">
        {luoghi.map((l) => (
          <Luogo key={l.id} l={l} en={en} />
        ))}
      </ul>
      {dati && dati.luoghi.length > VISIBILI && (
        <button type="button" className="dv-tutti" onClick={() => setTutti(!tutti)}>
          {tutti ? (en ? 'Show fewer' : 'Mostra meno') : en ? `Show all ${dati.luoghi.length}` : `Mostra tutti i ${dati.luoghi.length}`}
        </button>
      )}
      <p className="dv-fonte">
        {en ? 'Places' : 'Luoghi'}: © OpenStreetMap contributors · {en ? 'stops' : 'fermate'}: GTFS ANM ·{' '}
        {en ? 'opening hours: check the official website' : 'orari di apertura: verifica sul sito ufficiale'}
      </p>
    </section>
  )
}
