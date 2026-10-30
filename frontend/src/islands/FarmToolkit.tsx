import { ArrowUpRight, Sprout, MessageCircle, ChartNoAxesCombined, ScanLine, CloudSun, IndianRupee, BookOpen, FlaskConical } from 'lucide-react'
import SpotlightCard from '@/components/SpotlightCard'
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
export interface FarmTool { title: string; description: string; cta: string; href: string; icon: string }
const icons = [{ match: 'chat', Icon: MessageCircle }, { match: 'flower', Icon: Sprout }, { match: 'graph', Icon: ChartNoAxesCombined }, { match: 'camera', Icon: ScanLine }, { match: 'cloud', Icon: CloudSun }, { match: 'currency', Icon: IndianRupee }, { match: 'journal', Icon: BookOpen }, { match: 'droplet', Icon: FlaskConical }]
export default function FarmToolkit({ tools }: { tools: FarmTool[] }) {
  return <div className="premium-toolkit">{tools.map((tool, index) => {
    const Icon = icons.find(item => tool.icon.includes(item.match))?.Icon ?? Sprout
    return <SpotlightCard key={tool.href} theme={index === 0 ? 'dark' : 'light'} spotlightColor={index === 0 ? '#b8e7ac' : '#bfd6a9'} intensity={0.13} flare={false} proximity={40} className={`premium-tool-spotlight ${index === 0 ? 'premium-tool-featured' : ''}`}>
      <Card className="premium-tool-card"><CardHeader>
        <div className="premium-tool-top"><span className="premium-tool-icon"><Icon size={23} strokeWidth={1.65} aria-hidden="true" /></span><Badge variant="outline" className="premium-tool-number">{String(index + 1).padStart(2, '0')}</Badge></div>
        <CardTitle><h3>{tool.title}</h3></CardTitle><CardDescription>{tool.description}</CardDescription>
      </CardHeader><CardFooter><Button nativeButton={false} render={<a href={tool.href} />} variant="ghost" className="premium-tool-action">{tool.cta}<ArrowUpRight size={17} aria-hidden="true" /></Button></CardFooter></Card>
    </SpotlightCard>
  })}</div>
}
