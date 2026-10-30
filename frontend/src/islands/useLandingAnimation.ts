import { useEffect, type RefObject } from 'react'

export function useLandingAnimation(root: RefObject<HTMLElement | null>) {
  useEffect(() => {
    const media = matchMedia('(prefers-reduced-motion: reduce)')
    const desktop = matchMedia('(min-width: 900px) and (pointer: fine)')
    const connection = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection
    let generation = 0
    let disposed = false
    let cleanups: (() => void)[] = []
    const configure = async () => {
      const current = ++generation
      cleanups.splice(0).reverse().forEach(clean => clean())
      if (disposed || media.matches || connection?.saveData || !root.current) return
      const { gsap } = await import('gsap')
      const { ScrollTrigger } = await import('gsap/ScrollTrigger')
      if (disposed || current !== generation || !root.current) return
      gsap.registerPlugin(ScrollTrigger)
      const host = root.current
      const context = gsap.context(() => {
        gsap.fromTo(host.querySelectorAll('[data-gsap-hero]'), { y: 24 }, { y: 0, duration: .9, stagger: .1, ease: 'power3.out', clearProps: 'transform' })
        host.querySelectorAll('[data-gsap-reveal]').forEach(element => {
          gsap.fromTo(element, { y: 32 }, { y: 0, duration: .9, ease: 'power3.out', clearProps: 'transform', scrollTrigger: { trigger: element, start: 'top 92%', once: true } })
        })
        gsap.to(host.querySelector('[data-scroll-progress]'), { scaleX: 1, ease: 'none', scrollTrigger: { trigger: host, start: 'top top', end: 'bottom bottom', scrub: true } })
        if (desktop.matches) host.querySelectorAll('[data-field-drift]').forEach(element => {
          gsap.fromTo(element, { y: -20 }, { y: 25, ease: 'none', scrollTrigger: { trigger: element.parentElement, start: 'top bottom', end: 'bottom top', scrub: .7 } })
        })
      }, host)
      cleanups.push(() => context.revert())
      if (!desktop.matches) return
      try {
        const { default: LocomotiveScroll } = await import('locomotive-scroll')
        if (disposed || current !== generation) return
        const scroll = new LocomotiveScroll({ lenisOptions: { smoothWheel: true, lerp: .1, syncTouch: false, anchors: true, prevent: node => !node.closest('#chat-widget, .live-overlay, .navbar-collapse, [data-native-scroll]') } })
        const visibility = () => document.hidden ? scroll.stop() : scroll.start()
        document.addEventListener('visibilitychange', visibility)
        cleanups.push(() => { document.removeEventListener('visibilitychange', visibility); scroll.destroy() })
      } catch { /* Native scrolling remains available if enhancement cannot load. */ }
      const scene = host.querySelector<HTMLElement>('[data-field-scene]')
      if (!scene || (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4)) return
      try {
        const { createFieldLandscape } = await import('../field-landscape')
        if (disposed || current !== generation) return
        cleanups.push(createFieldLandscape(scene))
      } catch { /* Static field illustration remains visible without WebGL. */ }
    }
    const run = () => { void configure().catch(() => {}) }
    const leave = () => { generation++; cleanups.splice(0).reverse().forEach(clean => clean()) }
    const restore = (event: PageTransitionEvent) => { if (event.persisted) run() }
    media.addEventListener('change', run)
    desktop.addEventListener('change', run)
    window.addEventListener('pagehide', leave)
    window.addEventListener('pageshow', restore)
    run()
    return () => {
      disposed = true
      leave()
      media.removeEventListener('change', run)
      desktop.removeEventListener('change', run)
      window.removeEventListener('pagehide', leave)
      window.removeEventListener('pageshow', restore)
    }
  }, [root])
}
