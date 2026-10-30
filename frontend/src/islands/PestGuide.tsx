import { useEffect, useState } from 'react'
import { Leaf, ShieldCheck, Stethoscope } from 'lucide-react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/accordion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
interface Section { id: string; title: string; text: string }
function groupFor(id: string) { return id === 'prevention' ? 'prevention' : ['treat-now', 'organic-control', 'chemical-control'].includes(id) ? 'care' : 'symptoms' }
export default function PestGuide({ sections }: { sections: Section[] }) {
  const [tab, setTab] = useState(() => groupFor(location.hash.slice(1)))
  const [open, setOpen] = useState<string[]>(() => [location.hash.slice(1) || 'treat-now'])
  useEffect(() => {
    const followHash = () => {
      const id = location.hash.slice(1)
      if (!sections.some(section => section.id === id)) return
      setTab(groupFor(id)); setOpen([id])
      requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({ block: 'start' }))
    }
    window.addEventListener('hashchange', followHash)
    return () => window.removeEventListener('hashchange', followHash)
  }, [sections])
  const symptoms = sections.filter(section => groupFor(section.id) === 'symptoms')
  const care = sections.filter(section => groupFor(section.id) === 'care')
  const prevention = sections.find(section => section.id === 'prevention')
  return <Tabs value={tab} onValueChange={value => setTab(String(value))} className="premium-pest-guide">
    <TabsList className="premium-guide-tabs" aria-label="Crop care details"><TabsTrigger value="symptoms"><Stethoscope size={17} aria-hidden="true" />{symptoms[0]?.title}</TabsTrigger><TabsTrigger value="care"><Leaf size={17} aria-hidden="true" />{care[0]?.title}</TabsTrigger><TabsTrigger value="prevention"><ShieldCheck size={17} aria-hidden="true" />{prevention?.title}</TabsTrigger></TabsList>
    <TabsContent value="symptoms"><div className="premium-guide-overview">{symptoms.map(section => <Card key={section.id} id={section.id}><CardHeader><CardTitle><h2>{section.title}</h2></CardTitle></CardHeader><CardContent><p className="premium-reference-text">{section.text}</p></CardContent></Card>)}</div></TabsContent>
    <TabsContent value="care"><Accordion value={open} onValueChange={value => setOpen(value as string[])} className="premium-guide-accordion">{care.map(section => <AccordionItem key={section.id} value={section.id} id={section.id}><AccordionTrigger>{section.title}</AccordionTrigger><AccordionContent><p className="premium-reference-text">{section.text}</p></AccordionContent></AccordionItem>)}</Accordion></TabsContent>
    <TabsContent value="prevention">{prevention && <Card id={prevention.id}><CardHeader><CardTitle><h2>{prevention.title}</h2></CardTitle></CardHeader><CardContent><p className="premium-reference-text">{prevention.text}</p></CardContent></Card>}</TabsContent>
  </Tabs>
}
