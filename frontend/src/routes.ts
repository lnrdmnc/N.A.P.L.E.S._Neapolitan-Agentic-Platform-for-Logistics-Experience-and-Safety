// Route index: a new page is registered by adding one line here.
import type { ComponentType } from 'react'
import { Cittadino } from './cittadino'
import { ControlRoom } from './control-room'
import { Home } from './home/Home'

export const ROUTES: { path: string; Component: ComponentType }[] = [
  { path: '/', Component: Home },
  { path: '/control-room', Component: ControlRoom },
  { path: '/cittadino', Component: Cittadino },
]
