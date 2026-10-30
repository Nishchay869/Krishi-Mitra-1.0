import RotatingText from '@/components/RotatingText'
import SplitText from '@/components/SplitText'

interface HomeHeroProps {
  title: string
  languages: string[]
}

const prefersReducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

// Home page headline: React Bits SplitText (letter-by-letter reveal) + RotatingText cycling the
// languages the assistant speaks. Bootstrap classes keep it matching the rest of the Django page.
export default function HomeHero({ title, languages }: HomeHeroProps) {
  const still = prefersReducedMotion()
  return (
    <>
      {still ? (
        <h1 className="display-6 fw-semibold">{title}</h1>
      ) : (
        <SplitText
          text={title}
          tag="h1"
          className="display-6 fw-semibold"
          delay={35}
          duration={0.6}
          splitType="chars"
          from={{ opacity: 0, y: 30 }}
          to={{ opacity: 1, y: 0 }}
          textAlign="left"
        />
      )}
      <p className="lead mb-0 d-flex flex-wrap align-items-center gap-2">
        <span>Talk to it in</span>
        <RotatingText
          texts={languages}
          auto={!still}
          splitBy="words" /* whole words: splitting Indic scripts by character breaks conjuncts */
          rotationInterval={2200}
          mainClassName="inline-flex overflow-hidden rounded-lg bg-white/95 px-3 py-0.5 font-semibold text-[#1b5e20] shadow-sm"
          elementLevelClassName="inline-block"
          transition={{ type: 'spring', damping: 30, stiffness: 400 }}
          initial={{ y: '100%', opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: '-120%', opacity: 0 }}
        />
      </p>
    </>
  )
}
