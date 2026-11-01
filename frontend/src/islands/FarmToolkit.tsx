import { useEffect, useState } from 'react'
import { ArrowUpRight, Sprout, MessageCircle, ChartNoAxesCombined, ScanLine, CloudSun, IndianRupee, BookOpen, FlaskConical } from 'lucide-react'
import SpotlightCard from '@/components/SpotlightCard'
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export interface FarmTool {
  title: string
  description: string
  cta: string
  href: string
  icon: string
}

const icons = [
  { match: 'chat', Icon: MessageCircle },
  { match: 'flower', Icon: Sprout },
  { match: 'graph', Icon: ChartNoAxesCombined },
  { match: 'camera', Icon: ScanLine },
  { match: 'cloud', Icon: CloudSun },
  { match: 'currency', Icon: IndianRupee },
  { match: 'journal', Icon: BookOpen },
  { match: 'droplet', Icon: FlaskConical },
]

export default function FarmToolkit({ tools }: { tools: FarmTool[] }) {
  const [isDark, setIsDark] = useState<boolean>(() => {
    if (typeof document === 'undefined') return false
    return document.documentElement.classList.contains('dark')
  })

  useEffect(() => {
    if (typeof document === 'undefined') return
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains('dark'))
    })
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [])

  return (
    <div className="premium-toolkit">
      {tools.map((tool, index) => {
        const Icon = icons.find(item => tool.icon.includes(item.match))?.Icon ?? Sprout
        return (
          <SpotlightCard
            key={tool.href}
            theme={isDark ? 'dark' : 'light'}
            spotlightColor={isDark ? '#3b82f6' : '#93c5fd'}
            intensity={0.12}
            flare={false}
            proximity={40}
            className="premium-tool-spotlight"
          >
            <Card className="premium-tool-card flex flex-col h-full">
              <CardHeader className="p-0 mb-4">
                <div className="premium-tool-top">
                  <span className="premium-tool-icon">
                    <Icon size={22} strokeWidth={1.8} aria-hidden="true" />
                  </span>
                  <Badge variant="outline" className="premium-tool-number">
                    {String(index + 1).padStart(2, '0')}
                  </Badge>
                </div>
                <CardTitle>
                  <h3>{tool.title}</h3>
                </CardTitle>
                <CardDescription>
                  {tool.description}
                </CardDescription>
              </CardHeader>
              <CardFooter className="p-0 mt-auto pt-3">
                <a
                  href={tool.href}
                  className="btn-21st btn-21st-secondary btn-21st-sm w-full justify-between"
                >
                  <span className="font-bold">{tool.cta}</span>
                  <span className="btn-21st-icon-circle">
                    <ArrowUpRight size={15} strokeWidth={2.4} aria-hidden="true" />
                  </span>
                </a>
              </CardFooter>
            </Card>
          </SpotlightCard>
        )
      })}
    </div>
  )
}
