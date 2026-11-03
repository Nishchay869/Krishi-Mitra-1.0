import { lazy, Suspense, useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import {
  Plus,
  ArrowUpRight,
  ChevronRight,
  CloudSun,
  Check,
  AlertTriangle,
  AlertCircle,
  X,
  Bug,
  Sprout,
  Cpu,
  Bot
} from 'lucide-react'
import './AgroLanding.css'
import CropCursorEffect from './CropCursorEffect'
import DetailedLanding from './DetailedLanding'
import { experiences, type ExperienceKey } from './experience-content'

const IoTDashboard = lazy(() => import('./IoTDashboard'))

export interface CropStory {
  id: number | string
  title: string
  caption: string
  badge: string
  badge_key?: string
  image: string
  crop_name: string
  author: string
  created_at: string
  time_ago: string
}

export interface CropItem {
  id: string
  name: string
  display_name?: string
  image: string
  hasRing?: boolean
  has_ring?: boolean
  has_story?: boolean
  hasStory?: boolean
  stories?: CropStory[]
}

export type SprayStatus = 'DO_NOT_SPRAY' | 'POOR_CONDITIONS' | 'MARGINAL' | 'OPTIMAL'

export interface SprayConditionResult {
  status: SprayStatus
  deltaT: number
  wetBulb?: number
  reason: string
  deltaTRange?: '0-2' | '2-8' | '8-10' | '>10'
  deltaTStatus?: 'marginal' | 'optimal' | 'poor'
  rainRange?: 'no_rain' | '<0.1' | '>0.1'
  rainStatus?: 'optimal' | 'marginal' | 'poor'
  windRange?: '<12' | '12-25' | '>25'
  windStatus?: 'optimal' | 'marginal' | 'poor'
}

/**
 * Calculates Wet-Bulb Temperature using Stull's formula
 * @param temp - Dry bulb temperature in °C
 * @param rh - Relative humidity in % (0 - 100)
 * @returns Wet bulb temperature in °C
 */
export function calculateWetBulb(temp: number, rh: number): number {
  const tw =
    temp * Math.atan(0.151977 * Math.sqrt(rh + 8.313659)) +
    Math.atan(temp + rh) -
    Math.atan(rh - 1.676331) +
    0.00391838 * Math.pow(rh, 1.5) * Math.atan(0.023101 * rh) -
    4.686035
  return parseFloat(tw.toFixed(2))
}

/**
 * Evaluates spraying suitability for crops matching Plantix rules:
 * Delta T (°C): 0-2 (Marginal), 2-8 (Optimal), 8-10 (Marginal), >10 (Do Not Spray)
 * Rain (mm): No rain (Optimal), <0.1 (Marginal), >0.1 (Do Not Spray)
 * Wind (km/h): <12 (Optimal), 12-25 (Marginal), >25 (Do Not Spray)
 */
export function evaluateSprayCondition(
  temp: number,
  humidity: number,
  windSpeedKmH: number,
  rainWithin3Hours: boolean,
  _isDaylight?: boolean,
  _currentHour?: number,
  rainMm?: number
): SprayConditionResult {
  const wetBulb = calculateWetBulb(temp, humidity)
  const deltaT = parseFloat((temp - wetBulb).toFixed(2))
  const rainVal = rainMm !== undefined ? rainMm : (rainWithin3Hours ? 0.5 : 0.0)

  // 1. Delta T classification
  let deltaTRange: '0-2' | '2-8' | '8-10' | '>10' = '2-8'
  let deltaTStatus: 'marginal' | 'optimal' | 'poor' = 'optimal'
  let deltaTReason = 'Delta T is 2–8°C: ideal droplet retention and steady drying.'

  if (deltaT <= 2.0) {
    deltaTRange = '0-2'
    deltaTStatus = 'marginal'
    deltaTReason = 'Delta T is 0–2°C: slow drying and run-off risk.'
  } else if (deltaT > 2.0 && deltaT <= 8.0) {
    deltaTRange = '2-8'
    deltaTStatus = 'optimal'
    deltaTReason = 'Delta T is 2–8°C: ideal droplet retention and steady drying.'
  } else if (deltaT > 8.0 && deltaT <= 10.0) {
    deltaTRange = '8-10'
    deltaTStatus = 'marginal'
    deltaTReason = 'Delta T is 8–10°C: use coarse spray nozzles to reduce evaporation.'
  } else {
    deltaTRange = '>10'
    deltaTStatus = 'poor'
    deltaTReason = 'Air too dry (Delta T > 10°C): droplets evaporate before landing.'
  }

  // 2. Rain classification
  let rainRange: 'no_rain' | '<0.1' | '>0.1' = 'no_rain'
  let rainStatus: 'optimal' | 'marginal' | 'poor' = 'optimal'
  let rainReason = 'Dry weather prevents wash-off.'

  if (rainVal > 0.1 || rainWithin3Hours) {
    rainRange = '>0.1'
    rainStatus = 'poor'
    rainReason = 'Rain imminent (> 0.1 mm): pesticide will wash off.'
  } else if (rainVal > 0.0) {
    rainRange = '<0.1'
    rainStatus = 'marginal'
    rainReason = 'Trace rain (< 0.1 mm): monitor skies before spraying.'
  } else {
    rainRange = 'no_rain'
    rainStatus = 'optimal'
    rainReason = 'Dry weather prevents wash-off.'
  }

  // 3. Wind classification (Matching exact photo criteria: < 12, 12–25, > 25)
  let windRange: '<12' | '12-25' | '>25' = '<12'
  let windStatus: 'optimal' | 'marginal' | 'poor' = 'optimal'
  let windReason = 'Lower wind speeds (< 12 km/h) are ideal for better coverage and less spray drift.'

  if (windSpeedKmH < 12.0) {
    windRange = '<12'
    windStatus = 'optimal'
    windReason = 'Lower wind speeds (< 12 km/h) are ideal for better coverage and less spray drift.'
  } else if (windSpeedKmH >= 12.0 && windSpeedKmH <= 25.0) {
    windRange = '12-25'
    windStatus = 'marginal'
    windReason = 'Moderate wind (12–25 km/h): lower spray boom height and monitor drift.'
  } else {
    windRange = '>25'
    windStatus = 'poor'
    windReason = 'High wind (> 25 km/h): severe spray drift danger.'
  }

  // Plantix rules strictly driven by Delta T, Rain, and Wind
  if (deltaTStatus === 'poor') {
    return {
      status: 'DO_NOT_SPRAY',
      deltaT,
      wetBulb,
      reason: deltaTReason,
      deltaTRange,
      deltaTStatus,
      rainRange,
      rainStatus,
      windRange,
      windStatus
    }
  }

  if (rainStatus === 'poor') {
    return {
      status: 'DO_NOT_SPRAY',
      deltaT,
      wetBulb,
      reason: rainReason,
      deltaTRange,
      deltaTStatus,
      rainRange,
      rainStatus,
      windRange,
      windStatus
    }
  }

  if (windStatus === 'poor') {
    return {
      status: 'DO_NOT_SPRAY',
      deltaT,
      wetBulb,
      reason: windReason,
      deltaTRange,
      deltaTStatus,
      rainRange,
      rainStatus,
      windRange,
      windStatus
    }
  }

  if (deltaTStatus === 'marginal' || rainStatus === 'marginal' || windStatus === 'marginal') {
    const reason = deltaTStatus === 'marginal' ? deltaTReason : (windStatus === 'marginal' ? windReason : rainReason)
    return {
      status: 'MARGINAL',
      deltaT,
      wetBulb,
      reason,
      deltaTRange,
      deltaTStatus,
      rainRange,
      rainStatus,
      windRange,
      windStatus
    }
  }

  return {
    status: 'OPTIMAL',
    deltaT,
    wetBulb,
    reason: 'Ideal spraying window: Delta T 2–8°C, wind < 12 km/h, and dry weather.',
    deltaTRange,
    deltaTStatus,
    rainRange,
    rainStatus,
    windRange,
    windStatus
  }
}

export interface WeatherData {
  temp: number
  temp_str?: string
  humidity: number
  wind_kmh: number
  delta_t?: number
  rain_within_3h?: boolean
  is_daylight?: boolean
  status?: SprayStatus
  status_label?: string
  badge_class?: string
  badge_icon?: string
  time_text?: string
  reason?: string
  description?: string
  location?: string
}

export interface DiagnosisItem {
  id: number | string
  disease: string
  plant?: string
  date: string
  status_label: string
  status_type: 'complete' | 'incomplete'
  image_url: string
  url: string
}

type Routes = Record<string, string>
interface Props {
  routes: Routes
  assetBase: string
  userCrops?: CropItem[]
  weatherData?: WeatherData
  diagnoses?: DiagnosisItem[]
}

const t = (text: string) => {
  if (typeof window !== 'undefined') {
    const w = window as any
    if (typeof w.gettext === 'function') {
      const res = w.gettext(text)
      if (res && res !== text) return res
    }
    if (typeof w.django?.gettext === 'function') {
      const res = w.django.gettext(text)
      if (res && res !== text) return res
    }
    if (w.django?.catalog && typeof w.django.catalog[text] === 'string') {
      return w.django.catalog[text]
    }
  }
  return text
}

export default function AgroLanding(props: Props) {
  const key = new URLSearchParams(window.location.search).get('experience')
  if (key === 'iot') {
    return (
      <>
        <CropCursorEffect />
        <Suspense fallback={<div className="iot-loading" role="status">Loading field dashboard…</div>}>
          <IoTDashboard routes={props.routes} />
        </Suspense>
      </>
    )
  }
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
      <PlantixDashboard {...props} />
    </>
  )
}

function PlantixDashboard({ routes, assetBase, userCrops, weatherData, diagnoses }: Props) {
  const fallbackCrops: CropItem[] = [
    {
      id: 'tomato',
      name: 'Tomato',
      display_name: 'Tomato',
      image: `${assetBase}/crops/tomato.webp`,
      hasRing: true
    },
    {
      id: 'pepper-bell',
      name: 'Capsicum & Chilli',
      display_name: 'Capsicum & Chilli',
      image: `${assetBase}/crops/pepper-bell.webp`,
      hasRing: true
    },
    {
      id: 'rice',
      name: 'Rice',
      display_name: 'Rice',
      image: `${assetBase}/crops/rice.webp`,
      hasRing: false
    },
    {
      id: 'cotton',
      name: 'Cotton',
      display_name: 'Cotton',
      image: `${assetBase}/crops/cotton.webp`,
      hasRing: false
    },
    {
      id: 'wheat',
      name: 'Wheat',
      display_name: 'Wheat',
      image: `${assetBase}/crops/wheat.webp`,
      hasRing: false
    }
  ]

  const crops = userCrops && userCrops.length > 0 ? userCrops : fallbackCrops

  const [selectedCrop, setSelectedCrop] = useState<string>(crops[0]?.id || 'tomato')
  const [showSticky, setShowSticky] = useState<boolean>(false)

  // Instagram Story / Status Viewer State
  const [activeStoryCrop, setActiveStoryCrop] = useState<CropItem | null>(null)
  const [activeStoryIndex, setActiveStoryIndex] = useState<number>(0)
  const [isStoryPaused, setIsStoryPaused] = useState<boolean>(false)
  const [storyProgress, setStoryProgress] = useState<number>(0)
  const storyModalRef = useRef<HTMLDivElement>(null)

  // Enforce high-contrast text color on the Story modal elements
  useEffect(() => {
    if (!activeStoryCrop || !storyModalRef.current) return
    const el = storyModalRef.current

    const applyContrast = () => {
      el.querySelectorAll<HTMLElement>('*').forEach((node) => {
        if (node.classList.contains('instagram-story-badge-pill') || node.closest('.instagram-story-badge-pill')) {
          node.style.setProperty('color', '#4ade80', 'important')
        } else if (node.classList.contains('instagram-story-crop-meta') || node.closest('.instagram-story-crop-meta')) {
          node.style.setProperty('color', 'rgba(255, 255, 255, 0.9)', 'important')
        } else if (node.classList.contains('instagram-story-caption')) {
          node.style.setProperty('color', '#f1f5f9', 'important')
        } else if (node.classList.contains('instagram-story-verified-check')) {
          node.style.setProperty('color', '#ffffff', 'important')
          node.style.setProperty('background-color', '#3b82f6', 'important')
        } else if (node.tagName.toLowerCase() === 'svg' || node.tagName.toLowerCase() === 'path' || node.tagName.toLowerCase() === 'img') {
          // preserve graphics
        } else {
          node.style.setProperty('color', '#ffffff', 'important')
        }
      })
    }

    applyContrast()
    const id = requestAnimationFrame(applyContrast)
    const timer = setTimeout(applyContrast, 100)
    return () => {
      cancelAnimationFrame(id)
      clearTimeout(timer)
    }
  }, [activeStoryCrop, activeStoryIndex])

  useEffect(() => {
    if (!activeStoryCrop || !activeStoryCrop.stories || activeStoryCrop.stories.length === 0) {
      setStoryProgress(0)
      return
    }

    if (isStoryPaused) return

    const interval = setInterval(() => {
      setStoryProgress((prev) => {
        if (prev >= 100) {
          if (activeStoryIndex < (activeStoryCrop.stories?.length || 1) - 1) {
            setActiveStoryIndex((idx) => idx + 1)
            return 0
          } else {
            setActiveStoryCrop(null)
            setActiveStoryIndex(0)
            return 0
          }
        }
        return prev + 2
      })
    }, 100)

    return () => clearInterval(interval)
  }, [activeStoryCrop, activeStoryIndex, isStoryPaused])

  const handleNextStory = () => {
    if (!activeStoryCrop?.stories) return
    if (activeStoryIndex < activeStoryCrop.stories.length - 1) {
      setActiveStoryIndex((idx) => idx + 1)
      setStoryProgress(0)
    } else {
      setActiveStoryCrop(null)
      setActiveStoryIndex(0)
    }
  }

  const handlePrevStory = () => {
    if (activeStoryIndex > 0) {
      setActiveStoryIndex((idx) => idx - 1)
      setStoryProgress(0)
    }
  }

  const handleCropClick = (crop: CropItem) => {
    setSelectedCrop(crop.id)
    if (crop.stories && crop.stories.length > 0) {
      setActiveStoryCrop(crop)
      setActiveStoryIndex(0)
      setStoryProgress(0)
    }
  }

  const currentHour = new Date().getHours()
  const isNight =
    weatherData?.is_daylight === false ||
    (weatherData?.is_daylight === undefined && (currentHour < 6 || currentHour >= 18))

  const [currentWeather, setCurrentWeather] = useState<{
    temp: number
    humidity: number
    windKmH: number
    rainWithin3Hours: boolean
    is_daylight?: boolean
    location?: string
  }>(() => ({
    temp: Number(weatherData?.temp ?? (isNight ? 22 : 26)),
    humidity: Number(weatherData?.humidity ?? (isNight ? 70 : 55)),
    windKmH: Number(weatherData?.wind_kmh ?? (isNight ? 2.0 : 8.5)),
    rainWithin3Hours: Boolean(weatherData?.rain_within_3h ?? false),
    is_daylight: weatherData?.is_daylight ?? !isNight,
    location: weatherData?.location,
  }))

  const sprayResult = evaluateSprayCondition(
    currentWeather.temp,
    currentWeather.humidity,
    currentWeather.windKmH,
    currentWeather.rainWithin3Hours,
    currentWeather.is_daylight,
    currentHour
  )

  useEffect(() => {
    if (weatherData && weatherData.temp !== undefined) return
    const loc = currentWeather.location || 'Bengaluru'
    fetch(`/weather/api/?location=${encodeURIComponent(loc)}`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.forecast?.[0]?.slots?.[0]) {
          const slot = data.forecast[0].slots[0]
          const rainRaw = slot.rain
          const rainVal = typeof rainRaw === 'number' ? rainRaw : Number(rainRaw?.['3h'] ?? 0)
          setCurrentWeather({
            temp: Number(slot.temp ?? 24),
            humidity: Number(slot.humidity ?? 60),
            windKmH: Number((slot.wind ?? 2.5) * 3.6),
            rainWithin3Hours: rainVal > 0.1,
            is_daylight: slot.daylight,
            location: data.location,
          })
        }
      })
      .catch(() => {})
  }, [weatherData])

  // Format today's date respecting current locale (e.g. "1 Nov" or "1 ನವೆಂ")
  const currentLocale = typeof document !== 'undefined' ? (document.documentElement.lang || 'en') : 'en'
  const formattedDate = new Intl.DateTimeFormat(currentLocale === 'kn' ? 'kn-IN' : currentLocale, { day: 'numeric', month: 'short' }).format(new Date())

  const [tempUnit, setTempUnit] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('km_temp_unit') || 'C'
    }
    return 'C'
  })

  useEffect(() => {
    const handleUnitChange = (e: any) => {
      const u = e?.detail?.unit || localStorage.getItem('km_temp_unit') || 'C'
      setTempUnit(u)
    }
    window.addEventListener('km:temp_unit_change', handleUnitChange)
    window.addEventListener('storage', handleUnitChange)
    return () => {
      window.removeEventListener('km:temp_unit_change', handleUnitChange)
      window.removeEventListener('storage', handleUnitChange)
    }
  }, [])

  const formatTemperature = (celsius: number) => {
    if (tempUnit === 'F') {
      return `${Math.round(celsius * 1.8 + 32)} °F`
    }
    if (tempUnit === 'K') {
      return `${Math.round(celsius + 273.15)} K`
    }
    return `${Math.round(celsius)} °C`
  }

  const deltaTStr = tempUnit === 'F' ? `${(sprayResult.deltaT * 1.8).toFixed(1)}°F` : `${sprayResult.deltaT}°C`

  // Priority: Respect authoritative server evaluation (identical to /weather/ view)
  const serverStatus = weatherData?.status || sprayResult.status
  const serverLabel = weatherData?.status_label
  const serverBadge = weatherData?.badge_class
  const serverTimeText = weatherData?.time_text

  let statusLabel = serverLabel ? t(serverLabel) : t('Optimal')
  let statusBadgeClass = serverBadge || 'is-optimal'
  let StatusIcon = Check
  let timeSubtext = serverTimeText ? t(serverTimeText) : `ΔT ${deltaTStr} · ${t('Ideal window')}`

  if (serverStatus === 'OPTIMAL' || statusBadgeClass === 'is-optimal') {
    statusLabel = serverLabel ? t(serverLabel) : t('Optimal')
    statusBadgeClass = 'is-optimal'
    StatusIcon = Check
    timeSubtext = serverTimeText ? t(serverTimeText) : `ΔT ${deltaTStr} · ${t('Ideal window')}`
  } else if (
    serverStatus === 'MARGINAL' ||
    statusBadgeClass === 'is-marginal' ||
    statusBadgeClass === 'is-moderate'
  ) {
    statusLabel = serverLabel ? t(serverLabel) : t('Moderate')
    statusBadgeClass = statusBadgeClass.includes('moderate') ? 'is-moderate' : 'is-marginal'
    StatusIcon = AlertTriangle
    timeSubtext = serverTimeText ? t(serverTimeText) : `ΔT ${deltaTStr} · ${t('Monitor drift')}`
  } else if (serverStatus === 'POOR_CONDITIONS' || statusBadgeClass === 'is-poor') {
    statusLabel = serverLabel ? t(serverLabel) : t('Poor')
    statusBadgeClass = 'is-poor'
    StatusIcon = AlertCircle
    timeSubtext = serverTimeText ? t(serverTimeText) : `ΔT ${deltaTStr} · ${t('High humidity')}`
  } else {
    statusLabel = serverLabel ? t(serverLabel) : t('Avoid')
    statusBadgeClass = statusBadgeClass.includes('unfavourable') ? 'is-unfavourable' : 'is-avoid'
    StatusIcon = X
    if (serverTimeText) {
      timeSubtext = t(serverTimeText)
    } else if (isNight) {
      timeSubtext = t('Night time · Opens 06:00 AM')
    } else if (currentWeather.rainWithin3Hours) {
      timeSubtext = t('Rain imminent')
    } else if (currentWeather.windKmH > 25) {
      timeSubtext = t('High wind drift')
    } else if (currentWeather.temp > 35) {
      timeSubtext = t('High temperature')
    } else {
      timeSubtext = `ΔT ${sprayResult.deltaT}°C · ${t('Do not spray')}`
    }
  }

  useEffect(() => {
    const handleScroll = () => {
      // Show floating CTA once user scrolls past hero card (approx 280px)
      setShowSticky(window.scrollY > 280)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="plantix-dashboard" id="plantix-main">
      {/* Floating Sticky CTA on Scroll */}
      <AnimatePresence>
        {showSticky && (
          <motion.div
            className="plantix-floating-cta-wrap"
            initial={{ opacity: 0, y: -16, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -16, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            <a href={routes.disease || '/disease/detect/'} className="plantix-floating-btn">
              {t('Take a picture')}
            </a>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 1. Crop Selection Row */}
      <div className="plantix-crop-bar-wrap" aria-label={t('Your selected crops')}>
        <div className="plantix-crop-bar">
          {crops.map((crop, idx) => {
            const hasStory = Boolean(crop.has_story || crop.hasStory || (crop.stories && crop.stories.length > 0))
            const isSelected = selectedCrop === crop.id || (!selectedCrop && idx === 0)
            const hasRing = isSelected || crop.hasRing || crop.has_ring || hasStory
            const labelText = crop.display_name || crop.name
            return (
              <button
                key={crop.id + '-' + idx}
                type="button"
                className={`plantix-crop-item ${isSelected ? 'is-selected' : ''}`}
                onClick={() => handleCropClick(crop)}
                title={hasStory ? `${labelText} - Click to view status` : labelText}
              >
                <div className={`plantix-crop-avatar ${hasStory ? 'has-story-ring' : (hasRing ? 'has-ring' : '')}`}>
                  <img
                    src={crop.image}
                    alt={labelText}
                    loading="eager"
                    width="68"
                    height="68"
                  />
                  {hasStory && (
                    <span className="plantix-story-badge" title="Active status advisory">
                      <span className="plantix-story-badge-dot" />
                    </span>
                  )}
                </div>
                <span className="plantix-crop-label">{t(labelText)}</span>
              </button>
            )
          })}

          {/* Add Crop Button */}
          <a
            href={routes.profile || routes.library || '/accounts/profile/'}
            className="plantix-crop-add-item"
            title={t('Add or edit crops')}
            aria-label={t('Add or edit crops')}
          >
            <div className="plantix-crop-add-btn">
              <span className="plantix-add-icon-circle">
                <Plus size={22} strokeWidth={2.8} />
              </span>
            </div>
            <span className="plantix-crop-label plantix-add-label">{t('Add')}</span>
          </a>
        </div>
      </div>

      {/* 2. Weather & Spraying Conditions Card */}
      <div className="plantix-weather-card">
        {/* Left Subcard: Date, Weather Icon, Temperature */}
        <a href={routes.weather || '/weather/'} className="plantix-weather-left">
          <span className="plantix-weather-date">{formattedDate}</span>
          <div className="plantix-weather-icon">
            <CloudSun size={32} strokeWidth={1.7} />
          </div>
          <span className="plantix-weather-temp">{formatTemperature(currentWeather.temp)}</span>
        </a>

        {/* Right Subcard: Spraying Conditions */}
        <a
          href={routes.weather || '/weather/'}
          className="plantix-weather-right"
          title={`${sprayResult.reason} (Delta T: ${sprayResult.deltaT}°C)`}
        >
          <div className="plantix-spray-info">
            <span className="plantix-spray-title">{t('Spraying conditions')}</span>
            <span className="plantix-spray-status">{statusLabel}</span>
          </div>
          <div className="plantix-spray-time">{timeSubtext}</div>
          <div
            className={`plantix-spray-badge ${statusBadgeClass}`}
            aria-label={`${statusLabel}: ${sprayResult.reason}`}
          >
            <StatusIcon size={16} strokeWidth={2.8} />
          </div>
        </a>
      </div>

      {/* 3. Leaf Doctor / Diagnosis Hero Card */}
      <section className="plantix-hero-card" aria-labelledby="leaf-doctor-heading">
        <h2 id="leaf-doctor-heading" className="visually-hidden">{t('Leaf Doctor Diagnosis')}</h2>

        <div className="plantix-steps-row">
          {/* Step 1: Smartphone */}
          <div className="plantix-step-col">
            <div className="plantix-step-graphic">
              <svg width="44" height="60" viewBox="0 0 44 60" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <rect x="2" y="2" width="40" height="56" rx="8" stroke="#1e293b" strokeWidth="2.5" fill="#ffffff" />
                <rect x="6" y="8" width="32" height="42" rx="4" fill="#f8fafc" />
                <circle cx="22" cy="5" r="1.5" fill="#94a3b8" />
                {/* Seedling in phone */}
                <path d="M22 38V22" stroke="#16a34a" strokeWidth="2.2" strokeLinecap="round" />
                <path d="M22 28C18 26 15 22 16 18C20 18 22 22 22 25" fill="#4ade80" stroke="#16a34a" strokeWidth="1.2" />
                <path d="M22 25C24 23 27 20 29 21C29 25 26 27 22 28" fill="#22c55e" stroke="#16a34a" strokeWidth="1.2" />
              </svg>
            </div>
            <span className="plantix-step-label">{t('Take a picture')}</span>
          </div>

          <ChevronRight className="plantix-step-arrow" size={20} strokeWidth={2.4} aria-hidden="true" />

          {/* Step 2: Plant Seedling with Blue Checkmark */}
          <div className="plantix-step-col">
            <div className="plantix-step-graphic">
              <svg width="56" height="60" viewBox="0 0 56 60" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                <path d="M28 48V20" stroke="#16a34a" strokeWidth="2.8" strokeLinecap="round" />
                <path d="M28 32C20 30 14 24 16 18C22 18 27 24 28 28" fill="#4ade80" stroke="#16a34a" strokeWidth="1.8" />
                <path d="M28 26C36 24 42 18 40 12C34 12 29 18 28 22" fill="#22c55e" stroke="#16a34a" strokeWidth="1.8" />
                <path d="M28 20C28 12 22 6 22 6C22 6 30 8 32 16" fill="#86efac" stroke="#16a34a" strokeWidth="1.8" />
                {/* Circular blue checkmark */}
                <circle cx="38" cy="42" r="10" fill="#005bf6" stroke="#ffffff" strokeWidth="2" />
                <path d="M34 42L36.8 44.8L42.5 39" stroke="#ffffff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <span className="plantix-step-label">{t('See diagnosis')}</span>
          </div>

          <ChevronRight className="plantix-step-arrow" size={20} strokeWidth={2.4} aria-hidden="true" />

          {/* Step 3: Trigger Spray Bottle */}
          <div className="plantix-step-col">
            <div className="plantix-step-graphic">
              <svg width="56" height="60" viewBox="0 0 56 60" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                {/* Purple bottle body */}
                <path d="M19 28H37L39 52C39 54 37 56 35 56H21C19 56 17 54 17 52L19 28Z" fill="#a855f7" stroke="#7e22ce" strokeWidth="1.8" />
                {/* Neck */}
                <rect x="23" y="22" width="10" height="6" fill="#9333ea" stroke="#7e22ce" strokeWidth="1.2" />
                {/* Nozzle trigger */}
                <path d="M22 22V14H34V18H38L42 22H34V22" fill="#cbd5e1" stroke="#475569" strokeWidth="1.5" strokeLinejoin="round" />
                <path d="M22 14L15 22" stroke="#475569" strokeWidth="2.4" strokeLinecap="round" />
                <rect x="38" y="19" width="4" height="4" rx="1" fill="#3b82f6" />
                {/* Spray mist droplets */}
                <circle cx="47" cy="18" r="1.5" fill="#60a5fa" />
                <circle cx="50" cy="22" r="1.5" fill="#60a5fa" />
                <circle cx="46" cy="26" r="1.5" fill="#60a5fa" />
              </svg>
            </div>
            <span className="plantix-step-label">{t('Get medicine')}</span>
          </div>
        </div>

        {/* Primary Blue Button */}
        <a href={routes.disease || '/disease/detect/'} className="plantix-hero-cta">
          {t('Take a picture')}
        </a>
      </section>

      {/* 3b. Recent Diagnoses Carousel (Plantix style) */}
      {diagnoses && diagnoses.length > 0 && (
        <div className="plantix-diagnoses-carousel" aria-label={t('Recent diagnoses')}>
          {diagnoses.map((item) => (
            <a key={item.id} href={item.url} className="plantix-diag-card">
              <div className="plantix-diag-thumb-wrap">
                <img
                  src={item.image_url}
                  alt={item.disease}
                  className="plantix-diag-thumb"
                  width="60"
                  height="60"
                  loading="lazy"
                />
              </div>
              <div className="plantix-diag-content">
                <span className="plantix-diag-date">{item.date}</span>
                <h3 className="plantix-diag-title">{item.disease}</h3>
                <span className={`plantix-diag-badge ${item.status_type}`}>
                  {t(item.status_label)}
                </span>
              </div>
            </a>
          ))}
          <a
            href={routes.history || '/disease/history/'}
            className="plantix-diag-view-all-btn"
          >
            <span>{t('View all')}</span>
            <ChevronRight size={18} strokeWidth={2.5} />
          </a>
        </div>
      )}

      {/* 4. Tools Section */}
      <section className="plantix-section" aria-labelledby="tools-heading">
        <h2 id="tools-heading" className="plantix-section-title">{t('Tools')}</h2>
        <div className="plantix-tools-grid">
          {/* Tool 0: Farm Assistant */}
          <a href={routes.chat || '/chat/'} className="plantix-tool-card has-badge">
            <span className="plantix-badge-new">{t('AI')}</span>
            <div className="plantix-tool-icon">
              <Bot size={22} strokeWidth={2.2} color="#1e3a8a" />
            </div>
            <span className="plantix-tool-title">{t('Farm Assistant')}</span>
          </a>

          {/* Tool 1: Fertilizer calculator */}
          <a href={routes.fertilizer || '/crops/fertilizer/'} className="plantix-tool-card">
            <div className="plantix-tool-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1e3a8a" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M6 3h12l2 6v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9l2-6z" />
                <path d="M6 9h12" />
                <circle cx="12" cy="15" r="2.5" fill="#93c5fd" stroke="#1e3a8a" strokeWidth="1.5" />
              </svg>
            </div>
            <span className="plantix-tool-title">{t('Fertilizer calculator')}</span>
          </a>

          {/* Tool 2: Pesticide calculator */}
          <a href="/crops/pesticide/" className="plantix-tool-card">
            <div className="plantix-tool-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1e3a8a" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <rect x="5" y="10" width="14" height="11" rx="2" />
                <path d="M9 10V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v4" />
                <line x1="12" y1="2" x2="12" y2="4" />
                <path d="M12 14v3" />
              </svg>
            </div>
            <span className="plantix-tool-title">{t('Pesticide calculator')}</span>
          </a>

          {/* Tool 3: Farming calculator */}
          <a href={routes.yield || '/crops/yield/'} className="plantix-tool-card">
            <div className="plantix-tool-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1e3a8a" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <rect x="4" y="2" width="16" height="20" rx="3" />
                <line x1="8" y1="6" x2="16" y2="6" />
                <line x1="16" y1="14" x2="16" y2="18" />
                <path d="M16 10h.01" />
                <path d="M12 10h.01" />
                <path d="M8 10h.01" />
                <path d="M12 14h.01" />
                <path d="M8 14h.01" />
                <path d="M12 18h.01" />
                <path d="M8 18h.01" />
              </svg>
            </div>
            <span className="plantix-tool-title">{t('Farming calculator')}</span>
          </a>

          {/* Tool 4: Mandi prices */}
          <a href={routes.market || '/market/'} className="plantix-tool-card has-badge">
            <span className="plantix-badge-new">{t('New')}</span>
            <div className="plantix-tool-icon">
              <span className="plantix-rupee-sign" aria-hidden="true">₹</span>
            </div>
            <span className="plantix-tool-title">{t('Mandi prices')}</span>
          </a>

          {/* Tool 5: Crop Advisor */}
          <a href={routes.crop || '/crops/'} className="plantix-tool-card">
            <div className="plantix-tool-icon">
              <Sprout size={22} strokeWidth={2.2} color="#1e3a8a" />
            </div>
            <span className="plantix-tool-title">{t('Crop Advisor')}</span>
          </a>

          {/* Tool 6: IoT Sensors dashboard */}
          <a href={routes.iot || '/?experience=iot'} className="plantix-tool-card">
            <div className="plantix-tool-icon">
              <Cpu size={22} strokeWidth={2.2} color="#1e3a8a" />
            </div>
            <span className="plantix-tool-title">{t('IoT Sensors dashboard')}</span>
          </a>
        </div>
      </section>

      {/* 5. Library Section */}
      <section className="plantix-section" aria-labelledby="library-heading">
        <h2 id="library-heading" className="plantix-section-title">{t('Library')}</h2>
        <div className="plantix-library-grid">
          {/* Left Column */}
          <div className="plantix-lib-column">
            {/* Card 1: Crops */}
            <a href={routes.library || '/crops/library/'} className="plantix-lib-card card-crops">
              <span className="plantix-lib-title">{t('Crops')}</span>
              <div className="plantix-lib-icon-circle">
                <Sprout size={18} strokeWidth={2.4} color="#1e3a8a" />
              </div>
            </a>

            {/* Card 2: Cultivation Tips */}
            <a href={routes.library || '/crops/library/'} className="plantix-lib-card card-cultivation">
              <span className="plantix-lib-title">{t('Cultivation Tips')}</span>
              <div className="plantix-lib-icon-circle">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1e3a8a" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 22V8" />
                  <path d="M5 12H2a10 10 0 0 0 20 0h-3" />
                  <circle cx="12" cy="5" r="3" />
                </svg>
              </div>
            </a>
          </div>

          {/* Right Column */}
          <div className="plantix-lib-column">
            {/* Card 3: Pests & diseases */}
            <a href={routes.pests || '/crops/library/pests/'} className="plantix-lib-card card-pests">
              <span className="plantix-lib-title">{t('Pests & diseases')}</span>
              <div className="plantix-lib-icon-circle">
                <Bug size={18} strokeWidth={2.4} color="#1e3a8a" />
              </div>
            </a>

            {/* Card 4: Pests & Disease Alert */}
            <a href={routes.pests || '/crops/library/pests/'} className="plantix-lib-card card-alerts">
              <span className="plantix-lib-title">{t('Pests & Disease Alert')}</span>
              <div className="plantix-lib-icon-circle">
                <AlertTriangle size={18} strokeWidth={2.4} color="#1e3a8a" />
              </div>
            </a>
          </div>
        </div>
      </section>

      {/* 6. Sponsored / Advisory Banner */}
      <section className="plantix-sponsored-section" aria-labelledby="sponsored-label">
        <span id="sponsored-label" className="plantix-sponsored-label">{t('Sponsored')}</span>
        <a
          href={routes.chat || '/chat/'}
          className="plantix-sponsored-card"
          aria-label={t('One Home, One Chance — Build with confidence')}
        >
          <div className="plantix-sponsored-banner-top">
            <img
              src={`${assetBase}/landing/sponsored-banner-art.png`}
              alt="One Home, One Chance — Build with confidence"
              className="plantix-sponsored-img"
              loading="lazy"
              width="398"
              height="223"
            />
          </div>
          <div className="plantix-sponsored-footer">
            <div className="plantix-sponsored-footer-text">
              <span className="plantix-sponsored-footer-title">{t('One Home, One Chance')}</span>
              <span className="plantix-sponsored-footer-sub">{t('To build your identity')}</span>
            </div>
            <span className="plantix-sponsored-arrow">
              <ArrowUpRight size={22} strokeWidth={2.4} />
            </span>
          </div>
        </a>
      </section>

      {/* 7. Instagram-Style Crop Status Story Viewer Modal */}
      <AnimatePresence>
        {activeStoryCrop && activeStoryCrop.stories && activeStoryCrop.stories.length > 0 && (() => {
          const currentStory = activeStoryCrop.stories[activeStoryIndex] || activeStoryCrop.stories[0]
          return (
            <motion.div
              className="instagram-story-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={(e) => {
                if (e.target === e.currentTarget) {
                  setActiveStoryCrop(null)
                }
              }}
            >
              <motion.div
                ref={storyModalRef}
                className="instagram-story-modal"
                style={{ colorScheme: 'dark' }}
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.9, y: 20 }}
                transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                onMouseDown={() => setIsStoryPaused(true)}
                onMouseUp={() => setIsStoryPaused(false)}
                onTouchStart={() => setIsStoryPaused(true)}
                onTouchEnd={() => setIsStoryPaused(false)}
              >
                {/* Top Segmented Progress Bars */}
                <div className="instagram-story-progress-wrap">
                  {activeStoryCrop.stories.map((st, i) => {
                    const width = i < activeStoryIndex ? 100 : (i === activeStoryIndex ? storyProgress : 0)
                    return (
                      <div key={st.id + '-' + i} className="instagram-story-progress-bg">
                        <div
                          className="instagram-story-progress-fill"
                          style={{ width: `${width}%` }}
                        />
                      </div>
                    )
                  })}
                </div>

                {/* Story Top Header Bar */}
                <div className="instagram-story-header">
                  <div className="instagram-story-header-left">
                    <div className="instagram-story-crop-avatar">
                      <img src={activeStoryCrop.image} alt={activeStoryCrop.name} width="36" height="36" />
                    </div>
                    <div className="instagram-story-crop-info">
                      <div className="instagram-story-crop-name" style={{ color: '#ffffff' }}>
                        <span style={{ color: '#ffffff', textShadow: '0 2px 8px rgba(0,0,0,0.9)' }}>
                          {activeStoryCrop.display_name || activeStoryCrop.name}
                        </span>
                        <span className="instagram-story-verified-check" style={{ color: '#ffffff', backgroundColor: '#3b82f6' }}>✓</span>
                      </div>
                      <div className="instagram-story-crop-meta" style={{ color: 'rgba(255,255,255,0.9)' }}>
                        <span style={{ color: 'rgba(255,255,255,0.9)', textShadow: '0 1px 4px rgba(0,0,0,0.85)' }}>{currentStory.time_ago}</span>
                        <span style={{ color: 'rgba(255,255,255,0.7)' }}>·</span>
                        <span style={{ color: 'rgba(255,255,255,0.9)', textShadow: '0 1px 4px rgba(0,0,0,0.85)' }}>{currentStory.author}</span>
                      </div>
                    </div>
                  </div>

                  <div className="instagram-story-header-right">
                    <button
                      type="button"
                      className="instagram-story-close-btn"
                      onClick={() => setActiveStoryCrop(null)}
                      aria-label="Close story"
                      style={{ color: '#ffffff' }}
                    >
                      ✕
                    </button>
                  </div>
                </div>

                {/* Story Media (Photo / Advisory Picture) */}
                <div className="instagram-story-media-wrap">
                  <img
                    src={currentStory.image}
                    alt={currentStory.title}
                    className="instagram-story-media-img"
                  />
                </div>

                {/* Left/Right Tap Areas for Navigation */}
                <div className="instagram-story-tap-areas">
                  <div
                    className="instagram-story-tap-left"
                    onClick={(e) => {
                      e.stopPropagation()
                      handlePrevStory()
                    }}
                    title="Previous story"
                  />
                  <div
                    className="instagram-story-tap-right"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleNextStory()
                    }}
                    title="Next story"
                  />
                </div>

                {/* Bottom Frosted Advisory Card */}
                <div className="instagram-story-bottom-card" style={{ color: '#ffffff' }}>
                  <div
                    className="instagram-story-badge-pill"
                    style={{
                      color: '#4ade80',
                      backgroundColor: 'rgba(34, 197, 94, 0.28)',
                      borderColor: 'rgba(74, 222, 128, 0.7)',
                    }}
                  >
                    <span style={{ color: '#4ade80', textShadow: '0 1px 2px rgba(0,0,0,0.7)' }}>
                      {currentStory.badge}
                    </span>
                  </div>
                  <h3
                    className="instagram-story-title"
                    style={{
                      color: '#ffffff',
                      textShadow: '0 2px 10px rgba(0,0,0,0.95), 0 1px 4px rgba(0,0,0,0.9)',
                    }}
                  >
                    {currentStory.title}
                  </h3>
                  {currentStory.caption && (
                    <p
                      className="instagram-story-caption"
                      style={{
                        color: '#f1f5f9',
                        textShadow: '0 1px 6px rgba(0,0,0,0.9)',
                      }}
                    >
                      {currentStory.caption}
                    </p>
                  )}
                </div>
              </motion.div>
            </motion.div>
          )
        })()}
      </AnimatePresence>
    </div>
  )
}
