// Shown on every screen of the demo: every event in it is simulated.
export function SimulationBadge({ label = 'SIMULAZIONE' }: { label?: string }) {
  return (
    <span className="badge badge-simulated" role="status">
      {label}
    </span>
  )
}
