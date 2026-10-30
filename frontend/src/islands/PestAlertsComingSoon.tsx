import { BellRing, Cpu } from 'lucide-react'
const t = (text: string) => (window as Window & { gettext?: (s: string) => string }).gettext?.(text) ?? text
export default function PestAlertsComingSoon() {
  return <section className="pest-alerts-preview" aria-label={t('Pest & disease alerts — Coming soon')}>
    <span className="pest-alerts-icon" aria-hidden="true"><BellRing size={25} strokeWidth={1.5} /></span>
    <div className="pest-alerts-copy"><div className="pest-alerts-heading"><h2>{t('Pest & disease alerts')}</h2><span className="pest-alerts-badge">{t('Coming soon')}</span></div><p>{t('IoT integration is planned. Pest and disease alert notifications are not available yet.')}</p><span className="pest-alerts-plan"><Cpu size={14} aria-hidden="true" />{t('Planned feature · IoT integration')}</span></div>
  </section>
}
