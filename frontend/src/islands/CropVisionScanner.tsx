import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import {
  AlertTriangle,
  CheckCircle2,
  ShieldCheck,
  Calculator,
  RefreshCw,
  SwitchCamera,
  Maximize2,
  Droplets,
  Activity,
  Sparkles,
  Clock,
  FlaskConical,
  Focus,
  Upload,
  Camera,
  Image as ImageIcon
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import './CropVisionScanner.css'

interface SegmentationPolygon {
  class_id: number
  class_name: 'leaf' | 'disease_lesion' | 'pest_cluster' | string
  confidence: number
  polygon: [number, number][]
  bbox: [number, number, number, number]
  pixel_count: number
}

interface FrameQuality {
  focus_measure: number
  is_blurred: boolean
  is_acceptable: boolean
  status_message: string
  mean_luminance: number
}

interface PathologyMetrics {
  leaf_pixels: number
  lesion_pixels: number
  severity_index_pct: number
  calibrated_leaf_area_cm2: number
  pest_count: number
  pest_density_per_cm2: number
  lesion_count: number
  severity_stage: string
}

interface IPMRecommendation {
  target_name: string
  scientific_name: string
  category: 'pathogen' | 'pest'
  severity_stage: string
  active_agent: string
  formulation: string
  dilution_rate: string
  dilution_numeric: number
  dilution_unit: string
  application_method: string
  nozzle_type: string
  phi_days: number
  buffer_hours: number
  strategy_type: string
  tank_mix_compatibility: string
  action_plan_summary: string
}

interface DiagnosticResponse {
  success: boolean
  timestamp: number
  inference_time_ms: number
  quality: FrameQuality
  pathology?: PathologyMetrics
  diagnosed_target: string
  category: 'pathogen' | 'pest'
  polygons: SegmentationPolygon[]
  prescription?: IPMRecommendation
  stage_prescriptions?: Record<string, IPMRecommendation>
  alert_banner?: string
}

interface CropVisionScannerProps {
  isDark?: boolean
  initialCrop?: string
}

interface SampleLeafPreset {
  id: string
  name: string
  crop: string
  hint: string
  path: string
  description: string
}

const SAMPLE_LEAF_PRESETS: SampleLeafPreset[] = [
  {
    id: 'healthy_leaf',
    name: 'Healthy Foliage',
    crop: 'Tomato',
    hint: 'Healthy',
    path: '/static/images/pests/healthy-tomato.jpg',
    description: 'Vibrant chlorophyll, optimal turgor & zero necrosis'
  },
  {
    id: 'early_blight',
    name: 'Tomato Early Blight',
    crop: 'Tomato',
    hint: 'Early Blight',
    path: '/static/images/pests/tomato--early-blight.jpg',
    description: 'Alternaria solani concentric target rings'
  },
  {
    id: 'powdery_mildew',
    name: 'Powdery Mildew',
    crop: 'Chilli',
    hint: 'Powdery Mildew',
    path: '/static/images/pests/powdery-mildew.jpg',
    description: 'Whitish fungal powdery mycelium'
  },
  {
    id: 'rust',
    name: 'Leaf Rust (Puccinia)',
    crop: 'Maize',
    hint: 'Rust',
    path: '/static/images/pests/rust.jpg',
    description: 'Orange-brown raised spore pustules'
  },
  {
    id: 'aphids',
    name: 'Aphids Colony',
    crop: 'Cotton',
    hint: 'Aphids',
    path: '/static/images/pests/aphids.jpg',
    description: 'Dense sap-sucking insect clusters'
  },
  {
    id: 'spider_mites',
    name: 'Spider Mites',
    crop: 'Tomato',
    hint: 'Spider Mites',
    path: '/static/images/pests/spider-mites.jpg',
    description: 'Fine chlorotic stipples & webbing'
  },
  {
    id: 'late_blight',
    name: 'Late Blight (Phytophthora)',
    crop: 'Tomato',
    hint: 'Late Blight',
    path: '/static/images/pests/tomato--late-blight.jpg',
    description: 'Water-soaked greasy dark lesions'
  }
]

export default function CropVisionScanner({ isDark = true, initialCrop = 'Tomato' }: CropVisionScannerProps) {
  // Video & Canvas references
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const inFlightRef = useRef<boolean>(false)

  // Source Mode: 'camera' | 'sample' | 'upload'
  const [sourceMode, setSourceMode] = useState<'camera' | 'sample' | 'upload'>('camera')
  const [staticImageSrc, setStaticImageSrc] = useState<string | null>(null)
  const [activeSampleId, setActiveSampleId] = useState<string | null>(null)

  // Camera & Stream States
  const [isStreaming, setIsStreaming] = useState<boolean>(false)
  const [isRequestingCamera, setIsRequestingCamera] = useState<boolean>(false)
  const isMobile = typeof navigator !== 'undefined' && /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
  const [cameraFacing, setCameraFacing] = useState<'environment' | 'user'>(isMobile ? 'environment' : 'user')
  const [cameraError, setCameraError] = useState<string | null>(null)

  // Agronomic Configuration
  const [selectedCrop, setSelectedCrop] = useState<string>(initialCrop)
  const [targetHint, setTargetHint] = useState<string>('Auto')
  const [connectionMode, setConnectionMode] = useState<'WebSocket' | 'HTTP'>('HTTP')

  // Real-time Diagnosis Data
  const [diagnosis, setDiagnosis] = useState<DiagnosticResponse | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false)
  const [freezeFrame, setFreezeFrame] = useState<boolean>(false)
  const [scanNotice, setScanNotice] = useState<string | null>(null)

  // Active Stage Tab for IPM Protocol Card: 'detected' | 'stage_1' | 'stage_2' | 'stage_3'
  const [activeStageTab, setActiveStageTab] = useState<'detected' | 'stage_1' | 'stage_2' | 'stage_3'>('detected')

  // Tank Dilution Calculator
  const [tankVolumeLiters, setTankVolumeLiters] = useState<number>(15)

  // -------------------------------------------------------------------------
  // 1. Core Inference Dispatcher (HTTP + WebSocket)
  // -------------------------------------------------------------------------
  const sendFrameForInference = useCallback(
    async (base64Image: string, overrideHint?: string, overrideCrop?: string) => {
      if (inFlightRef.current) return
      inFlightRef.current = true
      setIsAnalyzing(true)

      const activeHint = overrideHint !== undefined ? overrideHint : targetHint
      const activeCrop = overrideCrop !== undefined ? overrideCrop : selectedCrop

      // Attempt WebSocket transmission if connected
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        try {
          wsRef.current.send(
            JSON.stringify({
              frame: base64Image,
              crop: activeCrop,
              target_hint: activeHint,
            })
          )
          return
        } catch (err) {
          console.warn('WS send failed, falling back to HTTP:', err)
        }
      }

      // HTTP Endpoint (supports /crops/api/crop-vision/diagnose/ and root fallback)
      try {
        const endpoint = '/crops/api/crop-vision/diagnose/'
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
          },
          body: JSON.stringify({
            frame: base64Image,
            crop_hint: activeCrop,
            target_hint: activeHint,
          }),
        })

        if (res.ok) {
          const data = (await res.json()) as DiagnosticResponse
          setDiagnosis(data)
          if (data.polygons && data.polygons.length > 0) {
            setScanNotice(null)
          }
        } else {
          console.warn('Diagnosis HTTP response error:', res.status)
        }
      } catch (err) {
        console.debug('HTTP diagnostic frame dropped:', err)
      } finally {
        inFlightRef.current = false
        setIsAnalyzing(false)
      }
    },
    [selectedCrop, targetHint]
  )

  // -------------------------------------------------------------------------
  // 2. Camera Lifecycle Management (Bulletproof macOS / iOS / Android Fallbacks)
  // -------------------------------------------------------------------------
  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
    setIsStreaming(false)
  }, [])

  const startCamera = useCallback(async () => {
    setCameraError(null)
    setIsRequestingCamera(true)
    setSourceMode('camera')
    setActiveSampleId(null)
    setStaticImageSrc(null)

    if (typeof navigator === 'undefined' || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      const isSecure = typeof window !== 'undefined' ? window.isSecureContext : true
      setCameraError(
        !isSecure
          ? 'Camera requires a secure connection (HTTPS or localhost:8000). On external network IPs, please use "Upload Photo" or switch to localhost.'
          : 'Camera device API is not supported in this browser. Please use "Upload Photo".'
      )
      setIsRequestingCamera(false)
      setIsStreaming(false)
      return
    }

    try {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
        streamRef.current = null
      }

      let stream: MediaStream | null = null

      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: { ideal: cameraFacing },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
          audio: false,
        })
      } catch (err1: any) {
        console.warn('Constrained getUserMedia failed, attempting basic fallback { video: true }:', err1)
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false,
          })
        } catch (err2: any) {
          throw err2
        }
      }

      if (!stream) {
        throw new Error('No video stream received from camera device.')
      }

      streamRef.current = stream

      const video = videoRef.current
      if (video) {
        video.srcObject = stream
        video.muted = true
        video.defaultMuted = true
        video.playsInline = true
        video.setAttribute('playsinline', 'true')
        video.setAttribute('muted', 'true')

        try {
          await video.play()
        } catch (playErr) {
          console.warn('video.play() promise handled:', playErr)
        }

        video.onloadedmetadata = async () => {
          try {
            await video.play()
          } catch (e) {
            console.warn('onloadedmetadata play error:', e)
          }
          if (canvasRef.current) {
            canvasRef.current.width = video.videoWidth || 640
            canvasRef.current.height = video.videoHeight || 480
          }
        }
      }

      setIsStreaming(true)
      setCameraError(null)
    } catch (err: any) {
      console.warn('Camera access unavailable or denied:', err)
      const isPermissionDenied = err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError'
      setCameraError(
        isPermissionDenied
          ? 'Camera permission denied. Please allow camera access in your browser address bar and click "Open Camera".'
          : `Camera error (${err.name || 'Unavailable'}): ${err.message || 'Please check device permissions or use "Upload Photo" below.'}`
      )
      setIsStreaming(false)
    } finally {
      setIsRequestingCamera(false)
    }
  }, [cameraFacing])

  const toggleCameraFacing = () => {
    setCameraFacing((prev) => (prev === 'environment' ? 'user' : 'environment'))
  }

  // Auto-attempt camera on mount
  useEffect(() => {
    startCamera()
    return () => {
      stopCamera()
    }
  }, [startCamera, stopCamera])

  // -------------------------------------------------------------------------
  // 3. WebSocket Setup (with Automatic Fallback)
  // -------------------------------------------------------------------------
  useEffect(() => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws/crop-diagnostics?crop=${encodeURIComponent(
      selectedCrop
    )}&target_hint=${encodeURIComponent(targetHint)}`

    let socket: WebSocket | null = null
    try {
      socket = new WebSocket(wsUrl)
      wsRef.current = socket

      socket.onopen = () => {
        setConnectionMode('WebSocket')
      }

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data) as DiagnosticResponse
          setDiagnosis(payload)
          inFlightRef.current = false
          setIsAnalyzing(false)
        } catch (e) {
          console.error('Error parsing diagnostic stream:', e)
        }
      }

      socket.onerror = () => {
        setConnectionMode('HTTP')
      }

      socket.onclose = () => {
        setConnectionMode('HTTP')
      }
    } catch (e) {
      setConnectionMode('HTTP')
    }

    return () => {
      if (socket) {
        socket.close()
      }
    }
  }, [selectedCrop, targetHint])

  // -------------------------------------------------------------------------
  // 4. Manual Frame Capture & Instant Diagnose Button
  // -------------------------------------------------------------------------
  const captureCurrentFrameWithHint = useCallback(
    (explicitHint?: string) => {
      if (sourceMode === 'camera' && videoRef.current) {
        const video = videoRef.current
        if (video.videoWidth > 0 && video.videoHeight > 0) {
          const offscreen = document.createElement('canvas')
          offscreen.width = video.videoWidth
          offscreen.height = video.videoHeight
          const ctx = offscreen.getContext('2d')
          if (ctx) {
            ctx.drawImage(video, 0, 0, offscreen.width, offscreen.height)
            const base64 = offscreen.toDataURL('image/jpeg', 0.88)
            sendFrameForInference(base64, explicitHint)
            setScanNotice('Frame captured. Analyzing digital leaf pathology...')
          }
        }
      } else if (staticImageSrc) {
        sendFrameForInference(staticImageSrc, explicitHint)
      }
    },
    [sourceMode, staticImageSrc, sendFrameForInference]
  )

  // -------------------------------------------------------------------------
  // 5. Sample Leaf Preset Selector
  // -------------------------------------------------------------------------
  const loadSampleLeaf = useCallback(
    (preset: SampleLeafPreset) => {
      stopCamera()
      setSourceMode('sample')
      setActiveSampleId(preset.id)
      setSelectedCrop(preset.crop)
      setTargetHint(preset.hint)
      setActiveStageTab('detected')
      setScanNotice(`Diagnosing ${preset.name} (${preset.description})...`)

      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => {
        const offscreen = document.createElement('canvas')
        offscreen.width = img.naturalWidth || 640
        offscreen.height = img.naturalHeight || 480
        const ctx = offscreen.getContext('2d')
        if (ctx) {
          ctx.drawImage(img, 0, 0, offscreen.width, offscreen.height)
          const base64 = offscreen.toDataURL('image/jpeg', 0.9)
          setStaticImageSrc(base64)

          if (canvasRef.current) {
            canvasRef.current.width = offscreen.width
            canvasRef.current.height = offscreen.height
          }

          // Pass preset.hint and preset.crop directly so no stale closure occurs
          sendFrameForInference(base64, preset.hint, preset.crop)
        }
      }
      img.src = preset.path
    },
    [stopCamera, sendFrameForInference]
  )

  // -------------------------------------------------------------------------
  // 6. Direct User File Upload / Drag & Drop
  // -------------------------------------------------------------------------
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    processImageFile(file)
  }

  const processImageFile = (file: File) => {
    stopCamera()
    setSourceMode('upload')
    setActiveSampleId(null)
    setActiveStageTab('detected')
    setScanNotice(`Analyzing uploaded leaf: ${file.name}...`)

    const reader = new FileReader()
    reader.onload = (event) => {
      const base64 = event.target?.result as string
      if (base64) {
        setStaticImageSrc(base64)

        const img = new Image()
        img.onload = () => {
          if (canvasRef.current) {
            canvasRef.current.width = img.naturalWidth || 640
            canvasRef.current.height = img.naturalHeight || 480
          }
        }
        img.src = base64

        sendFrameForInference(base64, targetHint)
      }
    }
    reader.readAsDataURL(file)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processImageFile(e.dataTransfer.files[0])
    }
  }

  // -------------------------------------------------------------------------
  // 7. Continuous Video Frame Ingestion Interval (~1.5 FPS)
  // -------------------------------------------------------------------------
  useEffect(() => {
    if (freezeFrame) return
    if (sourceMode !== 'camera' || !isStreaming) return

    const interval = setInterval(() => {
      if (videoRef.current) {
        const video = videoRef.current
        if (video.videoWidth > 0 && !video.paused) {
          const offscreen = document.createElement('canvas')
          offscreen.width = video.videoWidth || 640
          offscreen.height = video.videoHeight || 480
          const ctx = offscreen.getContext('2d')
          if (ctx) {
            ctx.drawImage(video, 0, 0, offscreen.width, offscreen.height)
            const base64 = offscreen.toDataURL('image/jpeg', 0.8)
            sendFrameForInference(base64)
          }
        }
      }
    }, 700)

    return () => clearInterval(interval)
  }, [sourceMode, isStreaming, freezeFrame, sendFrameForInference])

  // -------------------------------------------------------------------------
  // 8. Canvas Polygon Overlay Drawing (Green Leaf, Red Lesion, Magenta Pest)
  // -------------------------------------------------------------------------
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    if (!diagnosis || !diagnosis.polygons || diagnosis.polygons.length === 0) return

    const w = canvas.width
    const h = canvas.height

    const sortedPolygons = [...diagnosis.polygons].sort((a, b) => a.class_id - b.class_id)

    sortedPolygons.forEach((poly) => {
      if (!poly.polygon || poly.polygon.length < 3) return

      ctx.save()
      ctx.beginPath()

      const firstPt = poly.polygon[0]
      ctx.moveTo(firstPt[0] * w, firstPt[1] * h)

      for (let i = 1; i < poly.polygon.length; i++) {
        const pt = poly.polygon[i]
        ctx.lineTo(pt[0] * w, pt[1] * h)
      }
      ctx.closePath()

      if (poly.class_name === 'leaf') {
        ctx.strokeStyle = 'rgba(16, 185, 129, 0.95)'
        ctx.lineWidth = 3
        ctx.fillStyle = 'rgba(16, 185, 129, 0.12)'
        ctx.shadowColor = '#10b981'
        ctx.shadowBlur = 8
        ctx.fill()
        ctx.stroke()
      } else if (poly.class_name === 'disease_lesion') {
        ctx.strokeStyle = 'rgba(239, 68, 68, 1)'
        ctx.lineWidth = 2.5
        ctx.fillStyle = 'rgba(239, 68, 68, 0.45)'
        ctx.shadowColor = '#ef4444'
        ctx.shadowBlur = 8
        ctx.fill()
        ctx.stroke()
      } else if (poly.class_name === 'pest_cluster') {
        ctx.strokeStyle = 'rgba(192, 132, 252, 1)'
        ctx.lineWidth = 2
        ctx.fillStyle = 'rgba(192, 132, 252, 0.55)'
        ctx.shadowColor = '#c084fc'
        ctx.shadowBlur = 6
        ctx.fill()
        ctx.stroke()
      }

      ctx.restore()
    })
  }, [diagnosis])

  // -------------------------------------------------------------------------
  // 9. Computed Active Prescription & Tank Dilution Arithmetic
  // -------------------------------------------------------------------------
  // Determine which stage recommendation to display:
  const activePrescription = useMemo((): IPMRecommendation | null => {
    if (!diagnosis?.prescription) return null

    if (activeStageTab === 'detected' || !diagnosis.stage_prescriptions) {
      return diagnosis.prescription
    }
    return diagnosis.stage_prescriptions[activeStageTab] || diagnosis.prescription
  }, [diagnosis, activeStageTab])

  const calculatedChemicalDose = useMemo(() => {
    if (!activePrescription) return null
    const rate = activePrescription.dilution_numeric
    const totalDose = (rate * tankVolumeLiters).toFixed(1)
    const unit = activePrescription.dilution_unit.includes('ml') ? 'ml' : 'grams'
    return {
      total: totalDose,
      unit: unit,
      rate: rate,
      tankLiters: tankVolumeLiters,
    }
  }, [activePrescription, tankVolumeLiters])

  const getStageBadgeColor = (stage?: string) => {
    if (!stage) return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
    if (stage.includes('Stage 3') || stage.includes('Severe')) {
      return 'bg-red-500/25 text-red-400 border-red-500/50 animate-pulse'
    }
    if (stage.includes('Stage 2') || stage.includes('Moderate')) {
      return 'bg-amber-500/25 text-amber-400 border-amber-500/50'
    }
    return 'bg-emerald-500/25 text-emerald-400 border-emerald-500/50'
  }

  return (
    <div className={`crop-vision-scanner ${isDark ? 'vision-dark' : 'vision-light'}`}>
      
      {/* ─── SCANNER TOP CONTROLS & HUD HEADER ─── */}
      <div className="vision-header-row">
        <div className="vision-title-group">
          <div className="vision-live-tag">
            <span className="live-pulse-dot" />
            <span>REAL-TIME PLANT VISION</span>
            <span className="vision-stream-fps">
              {sourceMode === 'camera'
                ? isStreaming
                  ? `1.5 FPS · ${connectionMode}`
                  : 'CAMERA READY'
                : `${sourceMode.toUpperCase()} MODE`}
            </span>
            {isAnalyzing && (
              <span className="analyzing-pill">
                <RefreshCw size={12} className="animate-spin" /> Analyzing...
              </span>
            )}
          </div>
          <h2>Digital Pathology & IPM Advisory Scanner</h2>
          <p className="vision-subtitle">
            Specific stage-classified bio-fungicide and curative pesticide prescriptions per pathogen species.
          </p>
        </div>

        <div className="vision-header-actions">
          {/* Crop Selector */}
          <div className="vision-select-wrap">
            <span className="select-label">Crop:</span>
            <select
              value={selectedCrop}
              onChange={(e) => {
                const newCrop = e.target.value
                setSelectedCrop(newCrop)
                if (staticImageSrc) {
                  sendFrameForInference(staticImageSrc, targetHint, newCrop)
                }
              }}
              className="vision-target-select"
              aria-label="Select crop"
            >
              <option value="Tomato">Tomato</option>
              <option value="Cotton">Cotton</option>
              <option value="Chilli">Chilli / Pepper</option>
              <option value="Paddy">Paddy / Rice</option>
              <option value="Maize">Maize / Corn</option>
              <option value="General">General / All Crops</option>
            </select>
          </div>

          {/* Target Disease / Pest Selector */}
          <div className="vision-select-wrap">
            <span className="select-label">Suspected Pathogen / Pest:</span>
            <select
              value={targetHint}
              onChange={(e) => {
                const newHint = e.target.value
                setTargetHint(newHint)
                if (staticImageSrc) {
                  sendFrameForInference(staticImageSrc, newHint)
                } else if (sourceMode === 'camera') {
                  captureCurrentFrameWithHint(newHint)
                }
              }}
              className="vision-target-select"
              aria-label="Select target disease or pest"
            >
              <option value="Auto">✨ Auto-Detect (AI Computer Vision)</option>
              <optgroup label="Fungal & Bacterial Pathogens">
                <option value="Early Blight">Early Blight (Alternaria solani)</option>
                <option value="Late Blight">Late Blight (Phytophthora infestans)</option>
                <option value="Powdery Mildew">Powdery Mildew (Erysiphe spp.)</option>
                <option value="Downy Mildew">Downy Mildew (Pseudoperonospora)</option>
                <option value="Rust">Leaf Rust (Puccinia spp.)</option>
                <option value="Anthracnose">Anthracnose (Colletotrichum)</option>
                <option value="Bacterial Spot">Bacterial Leaf Spot (Xanthomonas)</option>
                <option value="Cercospora Leaf Spot">Cercospora Leaf Spot / Tikka</option>
                <option value="Healthy">Healthy Leaf Foliage</option>
              </optgroup>
              <optgroup label="Arthropod Pests">
                <option value="Aphids">Aphids (Aphis gossypii)</option>
                <option value="Spider Mites">Two-Spotted Spider Mites (Tetranychus)</option>
                <option value="Thrips">Thrips (Scirtothrips dorsalis)</option>
                <option value="Whiteflies">Whiteflies (Bemisia tabaci)</option>
              </optgroup>
            </select>
          </div>

          {/* Camera & Media Source Action Buttons */}
          <div className="vision-cam-buttons">
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              className="d-none"
              onChange={handleFileUpload}
              aria-label="Upload leaf photo"
            />

            <Button
              variant="outline"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              title="Upload leaf photo from device"
              className="btn-upload-leaf"
            >
              <Upload size={14} className="me-1" />
              <span>Upload Photo</span>
            </Button>

            {sourceMode !== 'camera' || !isStreaming ? (
              <Button
                variant="default"
                size="sm"
                onClick={startCamera}
                disabled={isRequestingCamera}
                className="btn-open-camera"
              >
                {isRequestingCamera ? (
                  <>
                    <RefreshCw size={14} className="me-1 animate-spin" />
                    <span>Opening...</span>
                  </>
                ) : (
                  <>
                    <Camera size={14} className="me-1" />
                    <span>Open Camera</span>
                  </>
                )}
              </Button>
            ) : (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleCameraFacing}
                  title="Switch between front and rear camera"
                  className="btn-cam-switch"
                >
                  <SwitchCamera size={14} />
                  <span>Flip ({cameraFacing === 'user' ? 'Front' : 'Back'})</span>
                </Button>

                <Button
                  variant={freezeFrame ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFreezeFrame((prev) => !prev)}
                  className={freezeFrame ? 'btn-frozen' : ''}
                >
                  {freezeFrame ? <RefreshCw size={14} className="animate-spin" /> : <Maximize2 size={14} />}
                  <span>{freezeFrame ? 'Resume' : 'Freeze'}</span>
                </Button>

                <Button
                  variant="default"
                  size="sm"
                  onClick={() => captureCurrentFrameWithHint(targetHint)}
                  className="btn-snap-frame"
                >
                  <Camera size={14} className="me-1" />
                  <span>Diagnose Frame</span>
                </Button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* ─── SAMPLE LEAF PRESETS QUICK-PICK BAR ─── */}
      <div className="vision-samples-bar">
        <span className="samples-bar-label">
          <ImageIcon size={14} className="text-emerald-400" />
          <span>Quick Test Leaf Samples:</span>
        </span>
        <div className="samples-chips-list">
          {SAMPLE_LEAF_PRESETS.map((preset) => (
            <button
              key={preset.id}
              type="button"
              className={`sample-leaf-chip ${activeSampleId === preset.id ? 'is-active' : ''}`}
              onClick={() => loadSampleLeaf(preset)}
              title={preset.description}
            >
              <span className="chip-indicator" />
              <span className="chip-name">{preset.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ─── BLUR QUALITY OR SCAN NOTIFICATION BANNER ─── */}
      {diagnosis?.quality?.is_blurred && (
        <div className="vision-alert-banner alert-blur" role="alert">
          <AlertTriangle size={18} className="me-2 text-amber-400 flex-shrink-0" />
          <div className="d-flex flex-column">
            <span>
              <strong>Soft focus advisory:</strong> {diagnosis.quality.status_message}
            </span>
            <span className="text-xs opacity-80">
              Hold camera steady or upload a direct leaf photo for optimal edge segmentation. Calculated metrics are displayed below.
            </span>
          </div>
          <span className="ms-auto text-xs opacity-75 font-mono">
            Var(∇²I): {diagnosis.quality.focus_measure.toFixed(1)} &lt; 100.0
          </span>
        </div>
      )}

      {scanNotice && (
        <div className="vision-notice-banner" role="status">
          <Sparkles size={16} className="text-emerald-400 me-2" />
          <span>{scanNotice}</span>
        </div>
      )}

      {/* ─── PRIMARY WORKSPACE GRID ─── */}
      <div className="vision-viewport-grid">
        
        {/* Left Column: Live Camera Video Stream / Static Image + Canvas Overlay */}
        <div className="vision-stream-column">
          <div
            className="vision-feed-wrapper"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            {/* Active Futuristic Scan Beam */}
            <div className={`vision-scan-beam ${isAnalyzing ? 'is-scanning' : ''}`} />

            {/* Video Element: ALWAYS mounted in DOM so ref and srcObject are never null */}
            <video
              ref={videoRef}
              playsInline
              muted
              autoPlay
              className="vision-video-el"
              style={{
                display: sourceMode === 'camera' && isStreaming ? 'block' : 'none'
              }}
            />

            {/* Mode 2: Static Sample or Uploaded Image */}
            {sourceMode !== 'camera' && staticImageSrc && (
              <img
                src={staticImageSrc}
                alt="Analyzed Crop Leaf"
                className="vision-static-img"
              />
            )}

            {/* Mode 1 Inactive / Camera Permission Prompt Overlay */}
            {sourceMode === 'camera' && !isStreaming && (
              <div className="vision-camera-prompt-card">
                <div className="camera-prompt-icon-ring">
                  <Camera size={36} className="text-emerald-400" />
                </div>
                <h3>Live Plant Vision Camera</h3>
                <p>
                  {cameraError ||
                    'Click "Open Camera" to activate your webcam or phone camera for real-time leaf diagnosis.'}
                </p>
                <div className="d-flex flex-wrap gap-2 justify-content-center mt-3">
                  <Button
                    size="default"
                    onClick={startCamera}
                    disabled={isRequestingCamera}
                    className="btn-start-camera-prominent"
                  >
                    {isRequestingCamera ? (
                      <>
                        <RefreshCw size={16} className="me-1.5 animate-spin" />
                        <span>Connecting Camera...</span>
                      </>
                    ) : (
                      <>
                        <Camera size={16} className="me-1.5" />
                        <span>Open Camera</span>
                      </>
                    )}
                  </Button>
                  <Button
                    size="default"
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Upload size={15} className="me-1.5" />
                    <span>Upload Leaf Photo</span>
                  </Button>
                  <Button
                    size="default"
                    variant="ghost"
                    onClick={() => loadSampleLeaf(SAMPLE_LEAF_PRESETS[0])}
                    className="text-emerald-400 hover:text-emerald-300"
                  >
                    <span>Test Sample Leaf</span>
                  </Button>
                </div>
              </div>
            )}

            {/* Polygon Instance Segmentation Canvas Overlay */}
            <canvas
              ref={canvasRef}
              width={640}
              height={480}
              className="vision-overlay-canvas"
            />

            {/* HUD Overlays on top of the viewport */}
            <div className="vision-hud-overlay">
              <div className="hud-top-row">
                <span className="hud-badge hud-focus">
                  <Focus size={13} />
                  <span>
                    Focus: {diagnosis?.quality?.focus_measure ? diagnosis.quality.focus_measure.toFixed(1) : 'Calibrating'}
                  </span>
                </span>
                <span className="hud-badge hud-clahe">
                  <Sparkles size={13} />
                  <span>CLAHE LAB: ON</span>
                </span>
                {diagnosis?.inference_time_ms && (
                  <span className="hud-badge hud-latency">
                    <Activity size={13} />
                    <span>{diagnosis.inference_time_ms} ms</span>
                  </span>
                )}
                <span className="hud-badge hud-mode">
                  {sourceMode === 'camera'
                    ? isStreaming
                      ? `CAMERA (${cameraFacing.toUpperCase()})`
                      : 'STANDBY'
                    : sourceMode === 'sample'
                    ? 'SAMPLE PRESET'
                    : 'UPLOADED PHOTO'}
                </span>
              </div>

              {/* Bounding Crosshairs / Target Reticle */}
              <div className="hud-reticle-box">
                <div className="reticle-corner reticle-tl" />
                <div className="reticle-corner reticle-tr" />
                <div className="reticle-corner reticle-bl" />
                <div className="reticle-corner reticle-br" />
                <div className="reticle-crosshair" />
              </div>

              {/* HUD Bottom Legend */}
              <div className="hud-bottom-legend">
                <span className="legend-item legend-leaf">
                  <span className="legend-box" /> Leaf Blade
                </span>
                <span className="legend-item legend-lesion">
                  <span className="legend-box" /> Lesions (Necrosis)
                </span>
                <span className="legend-item legend-pest">
                  <span className="legend-box" /> Pest Colonies
                </span>
              </div>
            </div>

          </div>

          {/* Quick Camera Fallback & Test Trigger Footer */}
          <div className="vision-feed-footer">
            <span className="text-xs text-muted-foreground">
              {sourceMode === 'camera'
                ? isStreaming
                  ? 'Position target leaf flat in center reticle with indirect natural lighting.'
                  : 'Click "Open Camera" above to begin scanning.'
                : 'Showing segmented pathology masks for the selected leaf image.'}
            </span>
            <div className="d-flex gap-2 align-items-center">
              {sourceMode !== 'camera' && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={startCamera}
                  className="text-xs text-primary"
                >
                  <Camera size={13} className="me-1" />
                  Switch to Live Camera
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Quantitative Pathology Metrics & Stage 1-3 IPM Prescription */}
        <div className="vision-metrics-column">
          
          {/* 1. Quantitative Surface Analytics Card */}
          <Card className="vision-card">
            <CardHeader className="pb-2">
              <div className="d-flex justify-content-between align-items-center">
                <CardTitle className="text-sm font-semibold d-flex align-items-center gap-1.5">
                  <Activity size={16} className="text-primary" />
                  <span>Digital Pathology Mathematics</span>
                </CardTitle>
                <span className={`badge-stage ${getStageBadgeColor(diagnosis?.pathology?.severity_stage)}`}>
                  {diagnosis?.pathology?.severity_stage || 'Stage 1 (Early / Trace)'}
                </span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="pathology-stats-grid">
                
                {/* Surface Lesion Severity Index */}
                <div className="pathology-stat-box stat-severity">
                  <span className="stat-label">Surface Lesion Severity</span>
                  <div className="stat-value-row">
                    <strong className="stat-number">
                      {diagnosis?.pathology?.severity_index_pct !== undefined
                        ? diagnosis.pathology.severity_index_pct.toFixed(1)
                        : '0.0'}%
                    </strong>
                    <span className="stat-formula">(Σ Lesion / Σ Leaf)</span>
                  </div>
                  <div className="stat-progress-bar">
                    <div
                      className="stat-progress-fill"
                      style={{
                        width: `${Math.min(100, (diagnosis?.pathology?.severity_index_pct || 0) * 3)}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Calibrated Leaf Area */}
                <div className="pathology-stat-box">
                  <span className="stat-label">Calibrated Leaf Area</span>
                  <strong className="stat-number">
                    {diagnosis?.pathology?.calibrated_leaf_area_cm2 || '0.0'}{' '}
                    <small className="text-xs text-muted-foreground font-normal">cm²</small>
                  </strong>
                  <span className="stat-subtext">Spatial 40 px/cm calibration</span>
                </div>

                {/* Pest Density Metric */}
                <div className="pathology-stat-box">
                  <span className="stat-label">Pest Density</span>
                  <strong className="stat-number">
                    {diagnosis?.pathology?.pest_density_per_cm2 || '0.0'}{' '}
                    <small className="text-xs text-muted-foreground font-normal">pests/cm²</small>
                  </strong>
                  <span className="stat-subtext">
                    Total Insects: {diagnosis?.pathology?.pest_count || 0}
                  </span>
                </div>

                {/* Lesion Patches */}
                <div className="pathology-stat-box">
                  <span className="stat-label">Lesion Count</span>
                  <strong className="stat-number">{diagnosis?.pathology?.lesion_count || 0}</strong>
                  <span className="stat-subtext">Discrete necrotic loci</span>
                </div>

              </div>
            </CardContent>
          </Card>

          {/* 2. Actionable IPM Advisory & Stage Chemical Dilution Calculator Card */}
          <Card className="vision-card prescription-card">
            <CardHeader className="pb-2">
              <div className="d-flex justify-content-between align-items-center">
                <CardTitle className="text-sm font-semibold d-flex align-items-center gap-1.5">
                  <ShieldCheck size={16} className="text-emerald-500" />
                  <span>
                    {activePrescription
                      ? `${activePrescription.severity_stage} IPM Prescription`
                      : 'IPM Prescription Protocol'}
                  </span>
                </CardTitle>
                <Badge variant="outline" className="border-emerald-500/40 text-emerald-400">
                  {activePrescription?.strategy_type || 'Biological Prophylactic'}
                </Badge>
              </div>
            </CardHeader>

            <CardContent>
              {activePrescription ? (
                <div className="prescription-content">

                  {/* Stage Escalation Toggle Tabs (Biological vs Protectant vs Curative) */}
                  <div className="prescription-stage-tabs">
                    <span className="stage-tabs-label">IPM Escalation:</span>
                    <div className="stage-tabs-buttons">
                      <button
                        type="button"
                        className={`btn-stage-tab ${activeStageTab === 'detected' ? 'is-active' : ''}`}
                        onClick={() => setActiveStageTab('detected')}
                      >
                        <span className="detected-stage-dot" />
                        <span>Detected ({diagnosis?.pathology?.severity_stage?.split(' ')[0] || 'Auto'})</span>
                      </button>
                      <button
                        type="button"
                        className={`btn-stage-tab ${activeStageTab === 'stage_1' ? 'is-active' : ''}`}
                        onClick={() => setActiveStageTab('stage_1')}
                      >
                        <span>Stage 1 (Bio)</span>
                      </button>
                      <button
                        type="button"
                        className={`btn-stage-tab ${activeStageTab === 'stage_2' ? 'is-active' : ''}`}
                        onClick={() => setActiveStageTab('stage_2')}
                      >
                        <span>Stage 2 (Protectant)</span>
                      </button>
                      <button
                        type="button"
                        className={`btn-stage-tab ${activeStageTab === 'stage_3' ? 'is-active' : ''}`}
                        onClick={() => setActiveStageTab('stage_3')}
                      >
                        <span>Stage 3 (Curative)</span>
                      </button>
                    </div>
                  </div>
                  
                  {/* Active Molecule / Bio-Agent Banner */}
                  <div className="prescription-hero-box">
                    <div className="prescription-hero-top">
                      <div>
                        <span className="active-agent-label">PRESCRIBED ACTIVE AGENT & MEDICINE:</span>
                        <h4 className="active-agent-name">{activePrescription.active_agent}</h4>
                        <span className="scientific-organism">
                          Target Diagnosed: <strong>{activePrescription.target_name}</strong> ({activePrescription.scientific_name})
                        </span>
                      </div>
                      <span className="formulation-pill">{activePrescription.formulation}</span>
                    </div>

                    <div className="prescription-badges-row">
                      <span className="safety-badge">
                        <Clock size={13} className="me-1 text-emerald-400" />
                        PHI: {activePrescription.phi_days} Days
                      </span>
                      <span className="safety-badge">
                        <ShieldCheck size={13} className="me-1 text-blue-400" />
                        Worker Re-Entry: {activePrescription.buffer_hours}h
                      </span>
                      <span className="safety-badge">
                        <Droplets size={13} className="me-1 text-cyan-400" />
                        Base Dose: {activePrescription.dilution_rate}
                      </span>
                    </div>
                  </div>

                  {/* Chemical & Bio-Agent Tank Dilution Calculator */}
                  <div className="tank-calculator-wrap">
                    <div className="d-flex justify-content-between align-items-center mb-1.5">
                      <span className="calc-title d-flex align-items-center gap-1">
                        <Calculator size={14} className="text-primary" />
                        <span>Knapsack Tank Dilution Calculator</span>
                      </span>
                      <span className="text-xs text-muted-foreground">Select your sprayer volume:</span>
                    </div>

                    <div className="tank-buttons-row">
                      {[5, 10, 15, 20, 100].map((vol) => (
                        <button
                          key={vol}
                          type="button"
                          className={`btn-tank-vol ${tankVolumeLiters === vol ? 'is-selected' : ''}`}
                          onClick={() => setTankVolumeLiters(vol)}
                        >
                          {vol} L
                        </button>
                      ))}
                      <div className="custom-tank-input">
                        <input
                          type="number"
                          min="1"
                          max="1000"
                          value={tankVolumeLiters}
                          onChange={(e) => setTankVolumeLiters(Math.max(1, Number(e.target.value) || 1))}
                          aria-label="Custom spray tank capacity in Liters"
                        />
                        <span>L</span>
                      </div>
                    </div>

                    {calculatedChemicalDose && (
                      <div className="tank-result-box">
                        <div className="d-flex justify-content-between align-items-center">
                          <span>Required Tank Mix Quantity:</span>
                          <strong className="dose-output">
                            {calculatedChemicalDose.total} {calculatedChemicalDose.unit}
                          </strong>
                        </div>
                        <p className="tank-formula-caption">
                          Mix exactly {calculatedChemicalDose.total} {calculatedChemicalDose.unit} into{' '}
                          {calculatedChemicalDose.tankLiters} Liters of clean water (at{' '}
                          {calculatedChemicalDose.rate} {activePrescription.dilution_unit}).
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Application Engineering & Nozzle Specification */}
                  <div className="prescription-meta-grid">
                    <div className="presc-meta-item">
                      <strong>Application Technique:</strong>
                      <p>{activePrescription.application_method}</p>
                    </div>
                    <div className="presc-meta-item">
                      <strong>Nozzle Specification:</strong>
                      <p>{activePrescription.nozzle_type}</p>
                    </div>
                  </div>

                  {/* Tank Mix Compatibility & Stewardship */}
                  <div className="tank-mix-note">
                    <strong>Tank Compatibility & Surfactant:</strong>
                    <p>{activePrescription.tank_mix_compatibility}</p>
                  </div>

                  {/* Action Plan Execution */}
                  <div className="action-plan-box">
                    <CheckCircle2 size={16} className="text-emerald-400 mt-0.5 flex-shrink-0" />
                    <p>{activePrescription.action_plan_summary}</p>
                  </div>

                </div>
              ) : (
                <div className="prescription-empty">
                  <FlaskConical size={32} className="text-muted-foreground mb-2" />
                  <p>Hold leaf steady in scanner reticle, upload a photo, or choose a sample leaf above.</p>
                </div>
              )}
            </CardContent>
          </Card>

        </div>

      </div>

    </div>
  )
}
