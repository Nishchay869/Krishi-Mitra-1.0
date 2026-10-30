import { Component, useEffect, useState, type ReactNode } from 'react'
import Strands from '@/components/Strands'

// Background of the live voice conversation (static/js/chat.js). The page sends
// `krishi:live` events with { state, level }; the strands breathe with the farmer's voice while
// listening and with the assistant's voice while speaking.

type LiveState = 'listening' | 'thinking' | 'speaking' | 'paused'
interface Look { amplitude: number; intensity: number; glow: number; opacity: number }

const LOOKS: Record<LiveState, Look> = {
  listening: { amplitude: 0.75, intensity: 0.55, glow: 2.4, opacity: 0.92 },
  thinking:  { amplitude: 0.50, intensity: 0.40, glow: 2.0, opacity: 0.80 },
  speaking:  { amplitude: 0.85, intensity: 0.60, glow: 2.8, opacity: 0.95 },
  paused:    { amplitude: 0.25, intensity: 0.18, glow: 1.4, opacity: 0.50 },
}
// How much the voice level (0-1) adds on top; boosted now that Strands is the sole visual.
const VOICE = { amplitude: 1.2, intensity: 0.35, glow: 1.0 }
// Farm palette: leaf greens, ripe wheat, irrigation water, dawn sky.
const COLORS = ['#A5D6A7', '#43A047', '#FFD54F', '#4DD0E1', '#81C784']
const SMOOTHING = 0.15 // fraction of the gap closed per frame; avoids jumpy waves

const prefersReducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

const hasWebGL2 = () => {
  try {
    return Boolean(document.createElement('canvas').getContext('webgl2'))
  } catch {
    return false
  }
}

// If WebGL fails mid-way, show nothing rather than breaking the conversation UI.
class SilentBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() { return { failed: true } }
  render() { return this.state.failed ? null : this.props.children }
}

export default function LiveStrands() {
  const [look, setLook] = useState<Look>(LOOKS.listening)
  const [enabled] = useState(() => !prefersReducedMotion() && hasWebGL2())

  useEffect(() => {
    if (!enabled) return
    let state: LiveState = 'listening'
    let level = 0
    let current = { ...LOOKS.listening }
    let raf = 0
    let lastFrame = 0

    const onLive = (e: Event) => {
      const detail = (e as CustomEvent<{ state?: LiveState; level?: number }>).detail
      if (detail.state && detail.state in LOOKS) state = detail.state
      if (typeof detail.level === 'number') level = Math.min(Math.max(detail.level, 0), 1)
    }
    const tick = (t: number) => {
      raf = requestAnimationFrame(tick)
      if (t - lastFrame < 33) return // ~30 updates/s is plenty for the props
      lastFrame = t
      const base = LOOKS[state]
      const voice = state === 'listening' || state === 'speaking' ? level : 0
      const target: Look = {
        amplitude: base.amplitude + voice * VOICE.amplitude,
        intensity: base.intensity + voice * VOICE.intensity,
        glow: base.glow + voice * VOICE.glow,
        opacity: base.opacity,
      }
      current = {
        amplitude: current.amplitude + (target.amplitude - current.amplitude) * SMOOTHING,
        intensity: current.intensity + (target.intensity - current.intensity) * SMOOTHING,
        glow: current.glow + (target.glow - current.glow) * SMOOTHING,
        opacity: current.opacity + (target.opacity - current.opacity) * SMOOTHING,
      }
      setLook(current)
    }
    window.addEventListener('krishi:live', onLive)
    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      window.removeEventListener('krishi:live', onLive)
    }
  }, [enabled])

  if (!enabled) return null
  return (
    <SilentBoundary>
      <Strands colors={COLORS} count={5} speed={0.4} thickness={0.9} scale={1.3} saturation={1.4} spread={1.2} waviness={1.1} taper={2.5} {...look} />
    </SilentBoundary>
  )
}
