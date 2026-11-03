import type { ComponentType } from 'react'
import './index.css'

// React "islands" inside Django pages. Each component is its own lazily loaded chunk, so a page
// only downloads what it shows.
//  * Static: <div data-react-island="HomeHero" data-props='{"title": "…"}'> mounts on page load;
//    server-rendered content inside the element is the fallback until React takes over.
//  * Dynamic: window.KrishiIslands.mount(el, 'LiveStrands') from plain JS (static/js/chat.js);
//    resolves to an unmount function.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Loader = () => Promise<{ default: ComponentType<any> }>

const islands: Record<string, Loader> = {
  AgroLanding: () => import('./islands/AgroLanding'),
  FarmToolkit: () => import('./islands/FarmToolkit'),
  PestGuide: () => import('./islands/PestGuide'),
  HomeHero: () => import('./islands/HomeHero'),
  LiveStrands: () => import('./islands/LiveStrands'),
  CropCursorEffect: () => import('./islands/CropCursorEffect'),
  AuthIsland: () => import('./islands/AuthIsland'),
  ImageSliderLoginDemo: () => import('./components/ui/demo'),
  AIChatIsland: () => import('./islands/AIChatIsland'),
  AIChatCard: () => import('./components/ui/ai-chat-card'),
  PesticideCalculator: () => import('./islands/PesticideCalculator'),
}

async function mount(el: HTMLElement, name: string, props: object = {}): Promise<() => void> {
  if (name === 'LiveStrands' && (matchMedia('(prefers-reduced-motion: reduce), (max-width: 767px)').matches || (navigator as Navigator & { connection?: { saveData?: boolean } }).connection?.saveData)) return () => {}
  const load = islands[name]
  if (!load) return () => {}
  const [{ default: Island }, { createRoot }, { createElement }] = await Promise.all([load(), import('react-dom/client'), import('react')])
  const root = createRoot(el)
  root.render(createElement(Island, props))
  return () => root.unmount()
}

declare global {
  interface Window { KrishiIslands?: { mount: typeof mount } }
}
window.KrishiIslands = { mount }

document.querySelectorAll<HTMLElement>('[data-react-island]').forEach((el) => {
  const islandName = el.dataset.reactIsland ?? ''
  let props: Record<string, any> = {}
  if (el.dataset.props) {
    try {
      props = JSON.parse(el.dataset.props)
    } catch (e) {
      console.warn('Failed to parse data-props for island', islandName, e)
    }
  }

  if (islandName === 'AIChatIsland') {
    const histScript = document.getElementById('chat-history-data')
    if (histScript && histScript.textContent) {
      try {
        props.initialHistory = JSON.parse(histScript.textContent)
      } catch (e) {
        console.warn('Failed to parse chat-history-data:', e)
      }
    }
    if (el.dataset.userName) {
      props.userName = el.dataset.userName
    }
    if (el.dataset.isWidget === 'true') {
      props.isWidget = true
    }
  }

  mount(el, islandName, props)
})

import "./experience"

// Keep the translated server fallback if the landing chunk cannot load.
const landing = document.querySelector<HTMLElement>('[data-agro-landing]')
if (landing) {
  let userCrops: any[] | undefined
  const cropsScript = document.getElementById('user-crops-data')
  if (cropsScript && cropsScript.textContent) {
    try {
      userCrops = JSON.parse(cropsScript.textContent)
    } catch (e) {
      console.error('Failed to parse user-crops-data script:', e)
    }
  } else if (landing.dataset.userCrops) {
    try {
      userCrops = JSON.parse(landing.dataset.userCrops)
    } catch (e) {
      console.error('Failed to parse userCrops dataset:', e)
    }
  }

  let weatherData: any | undefined
  const weatherScript = document.getElementById('weather-data')
  if (weatherScript && weatherScript.textContent) {
    try {
      weatherData = JSON.parse(weatherScript.textContent)
    } catch (e) {
      console.error('Failed to parse weather-data script:', e)
    }
  } else if (landing.dataset.weather) {
    try {
      weatherData = JSON.parse(landing.dataset.weather)
    } catch (e) {
      console.error('Failed to parse weather dataset:', e)
    }
  }

  let diagnoses: any[] | undefined
  const diagScript = document.getElementById('diagnoses-data')
  if (diagScript && diagScript.textContent) {
    try {
      diagnoses = JSON.parse(diagScript.textContent)
    } catch (e) {
      console.error('Failed to parse diagnoses-data script:', e)
    }
  } else if (landing.dataset.diagnoses) {
    try {
      diagnoses = JSON.parse(landing.dataset.diagnoses)
    } catch (e) {
      console.error('Failed to parse diagnoses dataset:', e)
    }
  }

  const { assetBase = '/static/images', ...routes } = landing.dataset
  void mount(landing, 'AgroLanding', { routes, assetBase, userCrops, weatherData, diagnoses }).catch((err) => {
    console.error('Failed to mount AgroLanding island:', err)
  })

  // Crop cursor effect: a hidden <div> appended next to the landing root so
  // the effect component can attach listeners to .km-hero / .agro-hero.
  if (!matchMedia('(prefers-reduced-motion: reduce), (hover: none)').matches) {
    const effectHost = document.createElement('div')
    effectHost.setAttribute('aria-hidden', 'true')
    landing.parentElement?.appendChild(effectHost)
    void mount(effectHost, 'CropCursorEffect').catch((err) => {
      console.error('Failed to mount CropCursorEffect island:', err)
    })
  }
}

// Reuse translated server-rendered copy and links; retain the native fallback if a chunk fails.
document.querySelectorAll<HTMLElement>('[data-farm-toolkit]').forEach(el => {
  const tools = Array.from(el.querySelectorAll<HTMLAnchorElement>('.tool-link')).map(link => ({
    title: link.querySelector('h3')?.textContent?.trim() ?? '',
    description: link.querySelector('p')?.textContent?.trim() ?? '',
    cta: link.querySelector('.tool-cta')?.textContent?.trim() ?? '',
    href: link.getAttribute('href') ?? '#', icon: link.querySelector('.tool-icon i')?.className ?? '',
  }))
  if (tools.length && !el.closest('[data-agro-landing]')) mount(el, 'FarmToolkit', { tools }).catch(() => {})
})
document.querySelectorAll<HTMLElement>('[data-pest-guide]').forEach(el => {
  const sections = Array.from(el.querySelectorAll<HTMLElement>('.pest-care')).map(section => ({
    id: section.id, title: section.querySelector('h2')?.textContent?.trim() ?? '',
    text: section.querySelector('div')?.innerText.trim() ?? '',
  }))
  if (sections.length) mount(el, 'PestGuide', { sections }).catch(() => {})
})
document.querySelectorAll<HTMLAnchorElement>('.site-nav .nav-link[href]').forEach(link => {
  if (new URL(link.href).pathname === location.pathname && !new URL(link.href).hash) link.setAttribute('aria-current', 'page')
})
