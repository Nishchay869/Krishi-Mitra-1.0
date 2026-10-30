import { useId, useRef, useState, type ElementType } from 'react'
import { ArrowRight, ArrowUpRight, BookOpen, Check, ClipboardList, CloudSun, Droplets, MessageCircle, ScanLine, Sprout, TrendingUp } from 'lucide-react'
import { toolGuides } from './tool-guides'
import './ToolHowTo.css'

const t = (text: string) => (window as Window & { gettext?: (s: string) => string }).gettext?.(text) ?? text
const icons: Record<string, ElementType> = { chat: MessageCircle, crop: Sprout, yield: TrendingUp, disease: ScanLine, weather: CloudSun, market: TrendingUp, fertilizer: Droplets, library: BookOpen }
export default function ToolHowTo({ routes, toolKeys, initialTool }: { routes: Record<string, string>; toolKeys?: readonly string[]; initialTool?: string }) {
  const guides = toolKeys ? toolKeys.map(key => toolGuides.find(guide => guide.key === key)).filter(guide => guide !== undefined) : toolGuides
  const [selected, setSelected] = useState(initialTool ?? guides[0].key)
  const current = guides.find(guide => guide.key === selected) ?? guides[0]
  const Icon = icons[current.key]
  const id = useId()
  const tabs = useRef<HTMLDivElement>(null)
  function move(index: number) {
    setSelected(guides[index].key)
    tabs.current?.querySelectorAll<HTMLButtonElement>('[role=tab]')[index]?.focus()
  }
  return <section id="how-to-tools" className="tool-howto agro-section" aria-labelledby={`${id}-heading`}>
    <div className="agro-wrap">
      <div className="agro-section-top" data-gsap-reveal><span className="agro-eyebrow">{t('A PRACTICAL GUIDE / FROM FIRST CLICK TO NEXT STEP')}</span><span className="agro-small">{t('Choose a tool. Follow the steps.')}</span></div>
      <div className="howto-heading" data-gsap-reveal><h2 id={`${id}-heading`}>{t('How to use')}<br /><em>{t('your farm tools.')}</em></h2><p>{t('Know what to bring, where to click, and what the result means. Select a tool below for its complete walkthrough. Sign in if the tool asks you to, then continue with the steps.')}</p></div>
      <div className="howto-layout">
        <div className="howto-sidebar"><div className="howto-tabs" ref={tabs} role="tablist" aria-label={t('Step-by-step tool guides')} aria-orientation="vertical">{guides.map((guide, index) => {
          const GuideIcon = icons[guide.key]
          return <button type="button" key={guide.key} id={`${id}-tab-${guide.key}`} role="tab" aria-selected={guide.key === current.key} aria-controls={`${id}-panel`} tabIndex={guide.key === current.key ? 0 : -1} onClick={() => setSelected(guide.key)} onKeyDown={event => {
            if (!['ArrowDown', 'ArrowUp', 'ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(event.key)) return
            event.preventDefault()
            move(event.key === 'Home' ? 0 : event.key === 'End' ? guides.length - 1 : (index + (event.key === 'ArrowDown' || event.key === 'ArrowRight' ? 1 : guides.length - 1)) % guides.length)
          }}><GuideIcon size={19} strokeWidth={1.5} /><span>{t(guide.title)}</span><ArrowRight size={15} /></button>
        })}</div><div className="howto-sidebar-note"><BookOpen size={18} /><p>{t('Start with the preparation checklist, follow the numbered steps, then open the tool when you are ready.')}</p></div></div>
        <div className="howto-panel" id={`${id}-panel`} role="tabpanel" aria-labelledby={`${id}-tab-${current.key}`} tabIndex={0}>
          <div className="howto-panel-heading"><span className="howto-tool-icon"><Icon size={25} strokeWidth={1.4} /></span><div><span className="agro-eyebrow">{t('YOUR STEP-BY-STEP GUIDE')}</span><h3>{t(current.title)}</h3><p>{t(current.summary)}</p></div><span className="howto-step-count">{current.steps.length} {t('steps')}</span></div>
          <div className="howto-prepare"><h4><ClipboardList size={16} />{t('Before you begin')}</h4><ul>{current.prepare.map(item => <li key={item}><Check size={14} />{t(item)}</li>)}</ul></div>
          <ol className="howto-steps">{current.steps.map((step, index) => <li key={step.title}><span className="howto-step-number" aria-hidden="true">{String(index + 1).padStart(2, '0')}</span><div><h4>{t(step.title)}</h4><p>{t(step.text)}</p></div></li>)}</ol>
          <div className="howto-example"><span className="agro-eyebrow">{t('A PRACTICAL EXAMPLE')}</span><p>{t(current.example)}</p></div>
          <div className="howto-result"><div><h4>{t('What you’ll get')}</h4><p>{t(current.result)}</p></div><a className="agro-button forest" href={routes[current.key]}>{t(current.button)}<ArrowUpRight size={17} /></a></div>
        </div>
      </div>
    </div>
  </section>
}
