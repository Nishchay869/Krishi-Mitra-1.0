import { lazy, Suspense, useRef, useState, type ReactNode } from 'react'
import { motion, useReducedMotion, useScroll, useTransform } from 'motion/react'
import { ArrowDown, ArrowRight, ArrowUpRight, BookOpen, Check, CloudSun, Droplets, Leaf, ScanLine, Sprout, TrendingUp, MessageCircle, Plus, Minus } from 'lucide-react'
import './AgroLanding.css'
import DetailedLanding, { ExperienceNav } from './DetailedLanding'
import { experiences, type ExperienceKey } from './experience-content'
import { useLandingAnimation } from './useLandingAnimation'
import ToolHowTo from './ToolHowTo'
import PestAlertsComingSoon from './PestAlertsComingSoon'
import CropCursorEffect from './CropCursorEffect'

const IoTDashboard = lazy(() => import('./IoTDashboard'))

type Routes = Record<string, string>
interface Props { routes: Routes; assetBase: string }
const t = (text: string) => (window as Window & { gettext?: (s: string) => string }).gettext?.(text) ?? text
function Reveal({ children, className = '' }: { children: ReactNode; className?: string }) {
  const reduced = useReducedMotion()
  return <motion.div className={className} initial={false} whileInView={reduced ? {} : { y: [22, 0], opacity: [0.5, 1] }} viewport={{ once: true, amount: 0.12 }} transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}>{children}</motion.div>
}
export default function AgroLanding(props: Props) {
  const key = new URLSearchParams(window.location.search).get('experience')
  if (key === 'iot') return (
    <>
      <CropCursorEffect />
      <Suspense fallback={<div className="iot-loading" role="status">Loading field dashboard…</div>}><IoTDashboard routes={props.routes} /></Suspense>
    </>
  )
  if (key && Object.prototype.hasOwnProperty.call(experiences, key)) {
    return (
      <>
        <CropCursorEffect />
        <DetailedLanding pageKey={key as ExperienceKey} {...props} />
      </>
    )
  }
  return (
    <>
      <CropCursorEffect />
      <AgroOverview {...props} />
    </>
  )
}
function AgroOverview({ routes, assetBase }: Props) {
  const root = useRef<HTMLDivElement>(null)
  useLandingAnimation(root)
  const hero = useRef<HTMLElement>(null)
  const reduced = useReducedMotion()
  const { scrollYProgress } = useScroll({ target: hero, offset: ['start start', 'end start'] })
  const y = useTransform(scrollYProgress, [0, 1], ['0%', '16%'])
  const [active, setActive] = useState('all')
  const [openFaq, setOpenFaq] = useState<number | null>(0)
  const tools = [
    { title: 'Crop Advisor', category: 'plan', label: 'PLAN WITH PURPOSE', copy: 'The right crop starts with your soil. Explore recommendations based on nutrients, climate, and growing conditions.', image: 'rice', icon: Sprout, route: 'crop', featured: true },
    { title: 'Disease Check', category: 'care', label: 'LOOK A LITTLE CLOSER', copy: 'Turn a leaf photo into a starting point for understanding plant health.', image: 'cotton', icon: ScanLine, route: 'disease' },
    { title: 'Weather & Advisory', category: 'plan', label: 'WORK WITH THE WEATHER', copy: 'See the forecast and find a better window for your next farm task.', image: 'sugarcane', icon: CloudSun, route: 'weather' },
    { title: 'Fertilizer Calculator', category: 'care', label: 'MAKE EVERY INPUT COUNT', copy: 'Translate nutrient recommendations into practical quantities for your field.', image: 'barley', icon: Droplets, route: 'fertilizer' },
  ]
  const faqs = [
    ['Where should I begin?', 'Start with a question in the farming assistant, or choose a tool for the task in front of you. Create an account when prompted to access your farm dashboard.'],
    ['Can I use it on my phone?', 'Yes. The tools and pages adapt to your screen, with touch-friendly controls. Live advice, account features, weather, and market prices need an internet connection.'],
    ['Does a leaf photo give a confirmed diagnosis?', 'A photo can help explore possible causes. Image quality and field conditions affect results. Confirm important treatment decisions with a local agricultural expert.'],
    ['Can I ask in my own language?', 'The assistant supports questions in multiple Indian languages. Ask naturally, and include your crop, location, and growing conditions for more useful context.'],
  ]
  return <div className="agro-landing" ref={root}>
    <div className="experience-progress" data-scroll-progress aria-hidden="true" />
    <section className="agro-hero" ref={hero} aria-labelledby="agro-title">
      <motion.img className="agro-hero-image" src={`${assetBase}/landing/farmland.jpg`} alt="Sunlight falling across green farmland and rolling hills" fetchPriority="high" width="1920" height="1280" style={{ y: reduced ? 0 : y }} />
      <div className="agro-shade" />
      <div className="agro-hero-content agro-wrap">
        <motion.div initial={false} animate={reduced ? {} : { y: [20, 0], opacity: [0.4, 1] }} transition={{ duration: 0.8 }}>
          <span className="agro-eyebrow"><span className="agro-dot" />{t('ROOTED IN KNOWLEDGE. GROWN WITH AI.')}</span>
          <h1 id="agro-title">{t('A smarter way')}<br />{t('to grow a')} <em>{t('better tomorrow.')}</em></h1>
          <p>{t('Your soil. Your crops. Your next harvest. Bring a little more clarity to every farming decision, with a companion that grows with you.')}</p>
          <div className="agro-actions"><a className="agro-button lime" href={routes.start}>{t('Let’s grow together')}<ArrowUpRight size={18} /></a><a className="agro-button glass" href="#tools">{t('Explore the tools')}<ArrowDown size={17} /></a></div>
        </motion.div>
      </div>
      <div className="agro-hero-bottom agro-wrap"><a href="#mission">{t('SCROLL TO EXPLORE')}<ArrowDown size={15} /></a><div className="agro-hero-note"><span className="agro-round-icon"><Sprout size={22} /></span><span>{t('Made for the hands')}<br /><strong>{t('that feed tomorrow.')}</strong></span></div><span className="agro-coordinate">{t('INDIAN ROOTS. NEW POSSIBILITIES.')}</span></div>
    </section>
    <ExperienceNav />
    <div className="agro-trust agro-wrap"><p>{t('One companion.')}<br /><strong>{t('Every growing season.')}</strong></p><span><MessageCircle />{t('Your language')}</span><span><Sprout />{t('Your growing conditions')}</span><span><BookOpen />{t('Knowledge with context')}</span><span><Leaf />{t('Your next step')}</span></div>
    <section className="overview-experiences agro-wrap agro-section" aria-labelledby="explore-title">
      <div className="agro-section-top" data-gsap-reveal><span className="agro-eyebrow">{t('FIND YOUR WAY INTO A BETTER SEASON')}</span><span className="agro-small">{t('Three journeys. One connected farm.')}</span></div>
      <h2 id="explore-title" data-gsap-reveal>{t('What’s growing')} <em>{t('on your mind?')}</em></h2>
      <div className="overview-experience-grid">{Object.entries(experiences).map(([key, page]) => <a href={`/?experience=${key}`} key={key} data-gsap-reveal><div className="overview-experience-image"><img src={`${assetBase}/crops/${page.image}.webp`} alt="" width="600" height="450" loading="lazy" /><span>{page.number}</span></div><div className="overview-experience-copy"><h3>{t(page.label)}<ArrowUpRight size={22} /></h3><p>{t(page.intro)}</p><span>{t('Explore the journey')}<ArrowRight size={15} /></span></div></a>)}</div>
    </section>
    <section id="mission" className="agro-mission agro-wrap agro-section">
      <Reveal><div className="agro-section-top"><span className="agro-eyebrow">{t('01 / A LITTLE CLARITY GOES A LONG WAY')}</span><span className="agro-small">{t('For the farmer. For the future.')}</span></div>
      <h2>{t('Better decisions today.')}<br />{t('Stronger roots for')} <em>{t('tomorrow.')}</em></h2>
      <div className="agro-mission-bottom"><div className="agro-leaf-mark"><Sprout strokeWidth={1} /></div><p>{t('Farming has always been a conversation with the land. Krishi Mitra brings crop knowledge, practical tools, and AI guidance into that conversation — so your next step feels a little clearer.')}</p><a className="agro-text-link" href={routes.chat}>{t('Meet your farming companion')}<ArrowUpRight size={19} /></a></div>
      <div className="agro-metrics"><div><strong>01<span>—</span>08</strong><p>{t('Connected tools for your farm')}</p></div><div><strong>{t('Your farm.')}</strong><p>{t('Advice starts with your context')}</p></div><div><strong>{t('Every season.')}</strong><p>{t('From the first seed to the next harvest')}</p></div></div></Reveal>
    </section>
    <section id="tools" className="agro-solutions agro-section"><div className="agro-wrap"><Reveal><div className="agro-section-top"><span className="agro-eyebrow">{t('02 / THE FARM TOOLKIT')}</span><span className="agro-small">{t('Practical tools. Real possibilities.')}</span></div><div className="agro-heading-row"><h2>{t('Less guesswork.')}<br /><em>{t('More growing.')}</em></h2><div><p>{t('A little insight for whatever the day brings.')}<br />{t('Choose what your farm needs today.')}</p><div className="agro-filters" role="group" aria-label={t('Filter farm tools')}>{[['all', 'All tools'], ['plan', 'Plan & grow'], ['care', 'Plant care']].map(([key, label]) => <button key={key} type="button" aria-pressed={active === key} onClick={() => setActive(key)}>{t(label)}</button>)}</div></div></div></Reveal>
      <div className="agro-bento">{tools.filter(tool => active === 'all' || tool.category === active).map(tool => <Reveal className={`agro-solution ${tool.featured ? 'featured' : ''}`} key={tool.route}><a href={routes[tool.route]}><img loading="lazy" decoding="async" src={`${assetBase}/crops/${tool.image}.webp`} alt="" width="800" height="600" /><div className="agro-card-shade" /><div className="agro-card-top"><span className="agro-card-tag"><tool.icon size={15} />{t(tool.label)}</span><span className="agro-card-arrow"><ArrowUpRight size={22} /></span></div><div className="agro-card-copy"><h3>{t(tool.title)}</h3><p>{t(tool.copy)}</p></div></a></Reveal>)}</div>
      <div className="agro-tool-links">{[[MessageCircle, 'chat', 'Ask Assistant'], [TrendingUp, 'market', 'Market Prices'], [Sprout, 'yield', 'Yield Estimate'], [BookOpen, 'library', 'Crop Library']].map(([Icon, key, title]) => { const ToolIcon = Icon as typeof Leaf; return <a href={routes[key as string]} key={key as string}><ToolIcon size={21} />{t(title as string)}<ArrowUpRight size={17} /></a> })}</div>
    </div></section>
    <div className="agro-wrap pest-alerts-landing"><PestAlertsComingSoon /></div>
    <ToolHowTo routes={routes} />
    <section id="growing" className="agro-growing agro-wrap agro-section"><Reveal className="agro-growing-photo"><img src={`${assetBase}/crops/rice.webp`} width="800" height="900" alt={t('Rice plants growing together in a field')} loading="lazy" decoding="async" /><span><Sprout size={22} />{t('Good things take growing.')}</span></Reveal><Reveal className="agro-growing-copy"><span className="agro-eyebrow">{t('03 / FROM QUESTION TO CONFIDENCE')}</span><h2>{t('A small step.')}<br />{t('A whole new')}<br /><em>{t('perspective.')}</em></h2><ol>{[['Tell us about your farm', 'Start with a question, a soil report, or a leaf photo.'], ['Find a little clarity', 'Explore practical guidance and the context behind it.'], ['Take your next step', 'Plan your crop, care for your plants, and prepare for harvest.']].map(([title, copy], i) => <li key={title}><span>0{i + 1}</span><div><h3>{t(title)}</h3><p>{t(copy)}</p></div></li>)}</ol><a className="agro-button forest" href={routes.chat}>{t('Ask your first question')}<ArrowUpRight size={18} /></a></Reveal></section>
    <section className="agro-library agro-section"><div className="agro-wrap"><Reveal><div className="agro-section-top"><span className="agro-eyebrow">{t('04 / KNOW WHAT YOU GROW')}</span><a className="agro-text-link" href={routes.library}>{t('Explore the crop library')}<ArrowUpRight size={18} /></a></div><h2>{t('Every crop has')}<br /><em>{t('a story to tell.')}</em></h2></Reveal><div className="agro-crops">{[['rice', 'Rice', 'From seedbed to golden harvest.'], ['cotton', 'Cotton', 'Care for every stage of growth.'], ['sugarcane', 'Sugarcane', 'Build knowledge from the roots up.']].map(([slug, title, copy]) => <Reveal key={slug}><a href={`${routes.library}${slug}/`}><div className="agro-crop-image"><img src={`${assetBase}/crops/${slug}.webp`} alt={t(title)} width="600" height="450" loading="lazy" decoding="async" /><span><ArrowUpRight size={22} /></span></div><h3>{t(title)}</h3><p>{t(copy)}</p></a></Reveal>)}</div></div></section>
    <section className="agro-faq agro-wrap agro-section"><Reveal><span className="agro-eyebrow">{t('A FEW THINGS YOU MIGHT BE WONDERING')}</span><div className="agro-faq-grid"><h2>{t('Good questions.')}<br /><em>{t('Clear answers.')}</em></h2><div>{faqs.map(([q, a], i) => <div className="agro-faq-item" key={q}><h3><button aria-expanded={openFaq === i} aria-controls={`agro-answer-${i}`} onClick={() => setOpenFaq(openFaq === i ? null : i)}>{t(q)}{openFaq === i ? <Minus size={18} /> : <Plus size={18} />}</button></h3><div id={`agro-answer-${i}`} hidden={openFaq !== i}><p>{t(a)}</p></div></div>)}</div></div></Reveal></section>
    <section className="agro-cta"><div className="agro-wrap"><Reveal><span className="agro-eyebrow"><Check size={15} />{t('YOUR NEXT SEASON STARTS HERE')}</span><h2>{t('Let’s grow something')}<br /><em>{t('better. Together.')}</em></h2><a className="agro-button lime" href={routes.start}>{t('Start your growing journey')}<ArrowUpRight size={18} /></a><p>{t('A little guidance. A lot of possibility.')}</p></Reveal><Leaf className="agro-cta-leaf" strokeWidth={0.5} aria-hidden="true" /></div></section>
    <div className="agro-endnote agro-wrap"><span><Sprout size={18} />{t('Rooted in care. Built for your farm.')}</span><a href="#agro-title">{t('Back to the top')}<ArrowRight size={16} style={{ transform: 'rotate(-90deg)' }} /></a></div>
  </div>
}
