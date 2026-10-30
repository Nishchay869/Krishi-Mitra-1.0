'use client'
/**
 * CropCursorEffect: Interactive crop sowing for KrishiMitra.
 * Triggers across the entire landing page hero fold (the area shown in the screenshot).
 * 
 * - Standard mouse cursor remains 100% visible and unobstructed.
 * - Seeds drop realistically from below the cursor towards the ground.
 * - Plants sprout upon landing, sway gently, and dissolve after 2 seconds.
 * - Only active in this hero section on the home page.
 */

import { useEffect, useRef } from 'react'

const THROTTLE_MS = 220 // Sowing interval
const FALL_MS = 800     // Realistic gravity fall
const GROW_MS = 700     // Spring sprout growth
const HOLD_MS = 2000    // Sprout lingers for ~2 seconds
const FADE_MS = 600     // Smooth dissolve

const SEEDS = ['🌾', '🌱', '🫘', '🌽', '🍃', '🌿', '🌻']
const PLANTS = ['🌱', '🌿', '🌾', '🍀', '🪴']

const rnd = (lo: number, hi: number) => lo + Math.random() * (hi - lo)

const STYLE_ID = 'km-crop-cursor-styles'

function ensureStyles() {
  if (document.getElementById(STYLE_ID)) return
  const s = document.createElement('style')
  s.id = STYLE_ID
  s.textContent = `
/* Ensure native cursor visibility across the entire hero */
.agro-hero,
.agro-hero * {
  cursor: auto;
}
.agro-hero a,
.agro-hero button,
.agro-hero [role="button"],
.agro-hero a * {
  cursor: pointer !important;
}

@keyframes kc-seed-drop {
  0% {
    transform: translate3d(0, 0, 0) rotate(0deg) scale(0.9);
    opacity: 1;
  }
  65% {
    transform: translate3d(var(--kc-drift-x), calc(var(--kc-fall-y) * 0.8), 0) rotate(var(--kc-rot)) scale(0.8);
    opacity: 0.95;
  }
  100% {
    transform: translate3d(var(--kc-drift-x), var(--kc-fall-y), 0) rotate(var(--kc-rot)) scale(0.65);
    opacity: 0;
  }
}

@keyframes kc-plant-sprout {
  0% {
    transform: translate3d(-50%, 0, 0) scaleY(0) scaleX(0.4);
    opacity: 0;
  }
  50% {
    transform: translate3d(-50%, -6px, 0) scaleY(1.15) scaleX(1.08);
    opacity: 1;
  }
  75% {
    transform: translate3d(-50%, 2px, 0) scaleY(0.96) scaleX(0.98);
    opacity: 1;
  }
  100% {
    transform: translate3d(-50%, 0, 0) scaleY(1) scaleX(1);
    opacity: 1;
  }
}

@keyframes kc-plant-sway {
  0%, 100% {
    transform: translate3d(-50%, 0, 0) rotate(-4deg);
  }
  50% {
    transform: translate3d(-50%, 0, 0) rotate(4deg);
  }
}

@keyframes kc-fade-out {
  0% {
    opacity: 1;
    transform: translate3d(-50%, 0, 0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate3d(-50%, -4px, 0) scale(0.85);
  }
}

.kc-seed {
  position: fixed;
  pointer-events: none !important;
  user-select: none !important;
  z-index: 99999;
  font-size: var(--kc-size);
  line-height: 1;
  will-change: transform, opacity;
  animation: kc-seed-drop var(--kc-dur) cubic-bezier(0.38, 0, 0.7, 1) forwards;
}

.kc-plant {
  position: fixed;
  pointer-events: none !important;
  user-select: none !important;
  z-index: 99998;
  font-size: var(--kc-size);
  line-height: 1;
  transform-origin: center bottom;
  opacity: 0;
  will-change: transform, opacity;
}

.kc-plant.is-growing {
  animation:
    kc-plant-sprout var(--kc-grow-dur) cubic-bezier(0.34, 1.56, 0.64, 1) forwards,
    kc-plant-sway 2.2s ease-in-out var(--kc-grow-dur) infinite;
}

.kc-plant.is-fading {
  animation: kc-fade-out var(--kc-fade-dur) ease-out forwards !important;
}

.kc-soil-patch {
  position: fixed;
  pointer-events: none !important;
  user-select: none !important;
  z-index: 99997;
  width: var(--kc-soil-w);
  height: 6px;
  border-radius: 50%;
  background: radial-gradient(ellipse at center, rgba(16, 185, 129, 0.5) 0%, rgba(5, 150, 105, 0.25) 50%, transparent 80%);
  transform: translate3d(-50%, 0, 0);
  opacity: 0;
  will-change: opacity;
}

.kc-soil-patch.is-growing {
  opacity: 0.9;
  transition: opacity 0.35s ease-out;
}

.kc-soil-patch.is-fading {
  opacity: 0;
  transition: opacity var(--kc-fade-dur) ease-out;
}
`
  document.head.appendChild(s)
}

export default function CropCursorEffect() {
  const lastSpawn = useRef(0)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true
    ensureStyles()

    const spawn = (cx: number, cy: number, heroBottom: number) => {
      const now = performance.now()
      if (now - lastSpawn.current < THROTTLE_MS) return
      lastSpawn.current = now

      const seedSize = Math.round(rnd(18, 25))
      const plantSize = Math.round(rnd(24, 32))
      const soilWidth = plantSize * 1.8

      // Spawn seed below cursor pointer (cy + 18) so cursor arrow remains completely visible
      const startX = cx
      const startY = cy + 18

      // Drop distance towards ground
      const naturalDrop = rnd(75, 130)
      const maxGround = Math.min(heroBottom - plantSize - 8, window.innerHeight - plantSize - 8)
      const groundY = Math.min(maxGround, startY + naturalDrop)
      const fallDist = Math.max(35, groundY - startY)
      const driftX = rnd(-14, 14)
      const rot = rnd(-22, 22)

      // 1. Falling seed
      const seed = document.createElement('div')
      seed.className = 'kc-seed'
      seed.textContent = SEEDS[Math.floor(Math.random() * SEEDS.length)]
      seed.style.cssText = [
        `left:${startX}px`,
        `top:${startY}px`,
        `--kc-size:${seedSize}px`,
        `--kc-fall-y:${fallDist}px`,
        `--kc-drift-x:${driftX}px`,
        `--kc-rot:${rot}deg`,
        `--kc-dur:${FALL_MS}ms`,
      ].join(';')

      document.body.appendChild(seed)

      // 2. On seed landing -> sprout plant & soil patch
      setTimeout(() => {
        if (!mountedRef.current) {
          seed.remove()
          return
        }
        seed.remove()

        const landX = startX + driftX
        const landY = groundY

        // Soil patch
        const soil = document.createElement('div')
        soil.className = 'kc-soil-patch'
        soil.style.cssText = [
          `left:${landX}px`,
          `top:${landY + 6}px`,
          `--kc-soil-w:${soilWidth}px`,
          `--kc-fade-dur:${FADE_MS}ms`,
        ].join(';')
        document.body.appendChild(soil)
        void soil.offsetWidth
        soil.classList.add('is-growing')

        // Plant sprout
        const plant = document.createElement('div')
        plant.className = 'kc-plant'
        plant.textContent = PLANTS[Math.floor(Math.random() * PLANTS.length)]
        plant.style.cssText = [
          `left:${landX}px`,
          `top:${landY - plantSize + 6}px`,
          `--kc-size:${plantSize}px`,
          `--kc-grow-dur:${GROW_MS}ms`,
          `--kc-fade-dur:${FADE_MS}ms`,
        ].join(';')
        document.body.appendChild(plant)
        void plant.offsetWidth
        plant.classList.add('is-growing')

        // 3. Dissolve after 2 seconds (HOLD_MS)
        setTimeout(() => {
          if (!mountedRef.current) {
            plant.remove()
            soil.remove()
            return
          }
          plant.classList.remove('is-growing')
          plant.classList.add('is-fading')
          soil.classList.remove('is-growing')
          soil.classList.add('is-fading')

          setTimeout(() => {
            plant.remove()
            soil.remove()
          }, FADE_MS + 50)
        }, HOLD_MS)
      }, FALL_MS)
    }

    const onPointerMove = (e: MouseEvent) => {
      // Find the hero element on the page
      const hero = document.querySelector<HTMLElement>('.agro-hero')
      if (!hero) return

      const rect = hero.getBoundingClientRect()
      // Active across the entire hero screen shown in the screenshot
      // (from top of window down to the hero bottom bar)
      if (
        e.clientY >= 0 &&
        e.clientY <= rect.bottom &&
        e.clientX >= rect.left &&
        e.clientX <= rect.right &&
        rect.bottom > 80
      ) {
        spawn(e.clientX, e.clientY, rect.bottom)
      }
    }

    window.addEventListener('mousemove', onPointerMove, { passive: true })

    return () => {
      mountedRef.current = false
      window.removeEventListener('mousemove', onPointerMove)
      document.querySelectorAll('.kc-seed, .kc-plant, .kc-soil-patch').forEach(el => el.remove())
    }
  }, [])

  return null
}
