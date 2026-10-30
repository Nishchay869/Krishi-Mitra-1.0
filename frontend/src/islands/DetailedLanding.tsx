import { useEffect, useRef, useState } from 'react'
import { ArrowDown, ArrowUpRight, ArrowRight, Check, Sprout, Leaf, ScanLine, CloudSun, BookOpen } from 'lucide-react'
import { experiences, type ExperienceKey } from './experience-content'
import { useLandingAnimation } from './useLandingAnimation'
import './DetailedLanding.css'
import ToolHowTo from './ToolHowTo'
import PestAlertsComingSoon from './PestAlertsComingSoon'

const t = (text: string) => (window as Window & { gettext?: (s: string) => string }).gettext?.(text) ?? text
export function ExperienceNav({ current }: { current?: ExperienceKey }) {
  return <nav className="experience-nav" aria-label={t('Explore farming experiences')}><div className="agro-wrap"><a href="/" className={!current ? 'selected' : ''} aria-current={!current ? 'page' : undefined}>{t('Overview')}</a>{Object.entries(experiences).map(([key, page]) => <a key={key} className={key === current ? 'selected' : ''} aria-current={key === current ? 'page' : undefined} href={`/?experience=${key}`}><span>{page.number}</span>{t(page.label)}<ArrowUpRight size={12} /></a>)}<a href="/?experience=iot">{t('IoT dashboard')}<span>DEMO</span></a><a className="howto-nav-link" href="#how-to-tools"><BookOpen size={13} />{t('How to use')}</a></div></nav>
}
export default function DetailedLanding({ pageKey, routes, assetBase }: { pageKey: ExperienceKey; routes: Record<string, string>; assetBase: string }) {
  const page = experiences[pageKey]
  const root = useRef<HTMLDivElement>(null)
  const [stage, setStage] = useState(0)
  const selected = page.stages[stage]
  const Icon = pageKey === 'grow' ? Sprout : pageKey === 'care' ? ScanLine : CloudSun
  useLandingAnimation(root)
  useEffect(() => {
    const title = document.title
    document.title = `${page.label} · Krishi Mitra`
    return () => { document.title = title }
  }, [page.label])
  function moveTab(index: number) {
    setStage(index)
    root.current?.querySelector<HTMLButtonElement>(`#journey-tab-${index}`)?.focus()
  }
  return <div ref={root} className={`agro-landing detail-landing detail-${page.theme}`}>
    <div className="experience-progress" data-scroll-progress aria-hidden="true" />
    <section className="detail-hero" aria-labelledby="detail-title"><div className="detail-hero-photo"><img src={`${assetBase}/crops/${page.image}.webp`} alt="" width="1200" height="900" fetchPriority="high" /></div><div className="agro-wrap detail-hero-grid"><div className="detail-hero-copy"><a href="/" className="detail-back" data-gsap-hero><ArrowRight size={14} />{t('Back to the overview')}</a><span className="agro-eyebrow" data-gsap-hero><span className="agro-dot" />{page.number} / {t(page.label).toUpperCase()}</span><h1 id="detail-title" data-gsap-hero>{t(page.title)}<br /><em>{t(page.accent)}</em></h1><p data-gsap-hero>{t(page.intro)}</p><div className="agro-actions" data-gsap-hero><a className="agro-button lime" href={routes[page.primary]}>{t(page.primaryLabel)}<ArrowUpRight size={17} /></a><a className="agro-button glass" href="#journey">{t('Explore the journey')}<ArrowDown size={17} /></a></div></div>
      <div className="detail-field" data-gsap-hero><div className="detail-field-top"><span><Icon size={14} />{t('A CLOSER LOOK AT YOUR FIELD')}</span><span className="agro-dot" /></div><div className="detail-field-canvas" data-field-scene><div className="detail-field-fallback" aria-hidden="true"><div className="field-grid" /><Sprout size={80} strokeWidth={1} /></div></div><div className="detail-field-bottom"><span>{t('Illustrative field study · 3D')}</span><span className="detail-pointer-hint">{t('Move to explore')} ↗</span></div></div>
    </div><div className="detail-hero-caption agro-wrap"><span>{t('PRACTICAL KNOWLEDGE. YOUR LOCAL CONTEXT.')}</span><a href="#principles">{t('Discover more')}<ArrowDown size={14} /></a></div></section>
    <ExperienceNav current={pageKey} />
    <section id="principles" className="agro-wrap agro-section detail-principles"><div className="detail-editorial" data-gsap-reveal><span className="agro-eyebrow">{t('01 / SEE THE BIGGER PICTURE')}</span><h2>{t(page.statement)}<br /><em>{t(page.statementAccent)}</em></h2><p>{t(page.description)}</p></div><div className="detail-pillars">{page.pillars.map(([title, copy], i) => <article key={title} data-gsap-reveal><span className="detail-index">0{i + 1}<Leaf size={18} /></span><h3>{t(title)}</h3><p>{t(copy)}</p></article>)}</div></section>
    <section id="journey" className="detail-journey agro-section"><div className="agro-wrap"><div className="agro-section-top" data-gsap-reveal><span className="agro-eyebrow">{t('02 / TURN KNOWLEDGE INTO A NEXT STEP')}</span><span className="agro-small">{t('Your practical walkthrough')}</span></div><div className="detail-journey-heading" data-gsap-reveal><h2>{t('One thoughtful step.')}<br /><em>{t('Then the next.')}</em></h2><p>{t('Explore each stage and open the tool when you are ready. Your field observations belong in the picture, too.')}</p></div>
      <div className="journey-tabs" role="tablist" aria-label={t('Farming journey stages')}>{page.stages.map((item, i) => <button key={item.title} id={`journey-tab-${i}`} role="tab" aria-selected={stage === i} aria-controls="journey-panel" tabIndex={stage === i ? 0 : -1} onClick={() => setStage(i)} onKeyDown={event => { if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) { event.preventDefault(); moveTab(event.key === 'Home' ? 0 : event.key === 'End' ? 2 : (stage + (event.key === 'ArrowRight' ? 1 : 2)) % 3) } }}><span>0{i + 1}</span>{t(item.title)}<ArrowUpRight size={16} /></button>)}</div>
      <div className="journey-panel" id="journey-panel" role="tabpanel" aria-labelledby={`journey-tab-${stage}`} tabIndex={0}><div className="journey-photo"><img data-field-drift src={`${assetBase}/crops/${page.image}.webp`} alt={t(`${page.label}: a view from the field`)} width="800" height="700" loading="lazy" /><span>{t('GROUNDED IN YOUR GROWING CONDITIONS')}</span></div><div className="journey-content" key={stage}><span className="agro-eyebrow">{t(selected.eyebrow)}</span><h3>{t(selected.title)}</h3><p>{t(selected.description)}</p><ul>{selected.items.map(item => <li key={item}><Check size={16} />{t(item)}</li>)}</ul><a className="agro-button lime" href={routes[selected.route]}>{t(selected.cta)}<ArrowUpRight size={17} /></a></div></div>
    </div></section>
    <section className="detail-tools agro-wrap agro-section"><div className="detail-tools-heading" data-gsap-reveal><span className="agro-eyebrow">{t('03 / YOUR CONNECTED TOOLKIT')}</span><h2>{t(page.featureTitle)}<br /><em>{t(page.featureAccent)}</em></h2></div><div className="detail-tool-grid">{page.features.map(([route, title, copy], i) => <a href={routes[route]} key={route} data-gsap-reveal><div><span>0{i + 1}</span><ArrowUpRight size={23} /></div><Icon size={32} strokeWidth={1.2} /><h3>{t(title)}</h3><p>{t(copy)}</p><span className="detail-tool-cta">{t('Open the tool')}<ArrowRight size={15} /></span></a>)}</div></section>
    <section className="detail-note agro-wrap" data-gsap-reveal><span className="detail-note-symbol"><BookOpen size={27} strokeWidth={1.2} /></span><div><span className="agro-eyebrow">{t('A QUESTION WORTH ASKING')}</span><h2>{t(page.question)}</h2><p>{t(page.answer)}</p></div></section>
    {pageKey === 'care' && <div className="agro-wrap pest-alerts-landing"><PestAlertsComingSoon /></div>}
    <ToolHowTo routes={routes} toolKeys={page.features.map(([key]) => key)} initialTool={page.primary} />
    <section className="detail-next agro-wrap agro-section"><div className="agro-section-top" data-gsap-reveal><span className="agro-eyebrow">{t('04 / KEEP EXPLORING')}</span><a href="/" className="agro-text-link">{t('Back to the overview')}<ArrowUpRight size={16} /></a></div><div className="detail-related">{Object.entries(experiences).filter(([key]) => key !== pageKey).map(([key, next]) => <a key={key} href={`/?experience=${key}`} data-gsap-reveal><img src={`${assetBase}/crops/${next.image}.webp`} alt="" loading="lazy" width="700" height="450" /><div><span className="agro-eyebrow">{next.number} / {t('EXPLORE THE POSSIBILITIES')}</span><h3>{t(next.label)}</h3><p>{t(next.intro)}</p><span className="detail-related-arrow"><ArrowUpRight size={22} /></span></div></a>)}</div></section>
    <section className="agro-cta"><div className="agro-wrap"><div data-gsap-reveal><span className="agro-eyebrow">{t('A LITTLE GUIDANCE. A LOT OF POSSIBILITY.')}</span><h2>{t(page.closing)}<br /><em>{t(page.closingAccent)}</em></h2><div className="agro-actions"><a className="agro-button lime" href={routes[page.primary]}>{t(page.primaryLabel)}<ArrowUpRight size={18} /></a><a className="agro-button glass" href={routes[page.secondary]}>{t(page.secondaryLabel)}<ArrowUpRight size={18} /></a></div></div><Leaf className="agro-cta-leaf" strokeWidth={.5} aria-hidden="true" /></div></section>
    <div className="agro-endnote agro-wrap"><span><Sprout size={18} />{t('Rooted in care. Built for your farm.')}</span><a href="#detail-title">{t('Back to the top')}<ArrowUpRight size={16} /></a></div>
  </div>
}
