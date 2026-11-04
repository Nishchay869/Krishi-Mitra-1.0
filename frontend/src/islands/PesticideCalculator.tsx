import * as React from "react";
import {
  ArrowLeft,
  Volume2,
  VolumeX,
  Plus,
  Minus,
  Search,
  Trash2,
  Check,
  ChevronDown,
  Info,
  Ruler,
  RefreshCw,
  Droplet,
  X,
  Sparkles,
  Calculator,
} from "lucide-react";
import { PESTICIDES_DATABASE } from "../data/pesticides-db";
import type {
  PesticideFormulation,
  FormulationCropUse,
  FormulationDiseaseTarget,
} from "../data/pesticides-db";

interface CropOption {
  name: string;
  emoji: string;
}

const CROPS: CropOption[] = [
  // ─── Primary Staples & Cash Crops ───
  { name: "Potato", emoji: "🥔" },
  { name: "Tomato", emoji: "🍅" },
  { name: "Rice", emoji: "🌾" },
  { name: "Wheat", emoji: "🌾" },
  { name: "Cotton", emoji: "☁️" },
  { name: "Chilli", emoji: "🌶️" },
  { name: "Dry chillies", emoji: "🌶️" },
  { name: "Onion", emoji: "🧅" },
  { name: "Maize", emoji: "🌽" },
  { name: "Sugarcane", emoji: "🎋" },
  { name: "Soybean", emoji: "🫘" },
  { name: "Groundnut", emoji: "🥜" },
  { name: "Brinjal", emoji: "🍆" },
  { name: "Cabbage", emoji: "🥬" },
  { name: "Cauliflower", emoji: "🥦" },
  { name: "Okra / Bhendi", emoji: "🌱" },
  { name: "Okra", emoji: "🌱" },
  { name: "Gram / Chickpea", emoji: "🫘" },
  { name: "Chickpea", emoji: "🫘" },
  { name: "Mustard", emoji: "🌼" },
  { name: "Rapeseed &Mustard", emoji: "🌼" },
  { name: "Garlic", emoji: "🧄" },
  { name: "Ginger", emoji: "🫚" },
  { name: "Turmeric", emoji: "🌿" },

  // ─── Plantation & Commercial Crops ───
  { name: "Tea", emoji: "🍵" },
  { name: "Coffee", emoji: "☕" },
  { name: "Arecanut", emoji: "🌴" },
  { name: "Cashewnut", emoji: "🥜" },
  { name: "Coconut", emoji: "🥥" },
  { name: "Jute", emoji: "🎋" },
  { name: "Cardamom", emoji: "🌿" },
  { name: "Black Pepper", emoji: "🌿" },
  { name: "Black pepper", emoji: "🌿" },
  { name: "Coriander", emoji: "🌿" },

  // ─── Pulses & Legumes ───
  { name: "Pigeonpea / Pulses", emoji: "🫘" },
  { name: "Pigeonpeas", emoji: "🫘" },
  { name: "Blackgram", emoji: "🫘" },
  { name: "Mungbean", emoji: "🫘" },
  { name: "Lentil", emoji: "🫘" },
  { name: "Kidneybeans", emoji: "🫘" },
  { name: "Cowpea(Lobia)", emoji: "🫘" },
  { name: "Pea / Pulses", emoji: "🫛" },

  // ─── Cereals & Millets ───
  { name: "Bajra", emoji: "🌾" },
  { name: "Jowar", emoji: "🌾" },
  { name: "Ragi", emoji: "🌾" },
  { name: "Barley", emoji: "🌾" },

  // ─── Oilseeds ───
  { name: "Sunflower", emoji: "🌻" },
  { name: "Sesamum", emoji: "🌱" },
  { name: "Castor seed", emoji: "🌱" },
  { name: "Safflower", emoji: "🌼" },
  { name: "Linseed", emoji: "🌾" },

  // ─── Vegetables ───
  { name: "Pepper bell", emoji: "🫑" },
  { name: "Cucumber", emoji: "🥒" },
  { name: "Squash", emoji: "🥒" },
  { name: "Pumpkin", emoji: "🎃" },
  { name: "Sweet potato", emoji: "🍠" },
  { name: "Carrot", emoji: "🥕" },
  { name: "Vegetables (General)", emoji: "🥦" },

  // ─── Fruits ───
  { name: "Mango", emoji: "🥭" },
  { name: "Banana", emoji: "🍌" },
  { name: "Citrus", emoji: "🍊" },
  { name: "Orange", emoji: "🍊" },
  { name: "Grapes", emoji: "🍇" },
  { name: "Pomegranate", emoji: "🍎" },
  { name: "Apple", emoji: "🍎" },
  { name: "Guava", emoji: "🍐" },
  { name: "Papaya", emoji: "🍈" },
  { name: "Watermelon", emoji: "🍉" },
  { name: "Muskmelon", emoji: "🍈" },
  { name: "Pineapple", emoji: "🍍" },
  { name: "Strawberry", emoji: "🍓" },
  { name: "Litchi", emoji: "🍒" },
  { name: "Peach", emoji: "🍑" },
  { name: "Jackfruit", emoji: "🍈" },

  // ─── Flowers & Floriculture ───
  { name: "Rose", emoji: "🌹" },
  { name: "Marigold", emoji: "🌼" },
  { name: "Jasmine", emoji: "🌸" },
  { name: "Hibiscus", emoji: "🌺" },
  { name: "Tuberose", emoji: "💮" },
  { name: "Lotus", emoji: "🪷" },

  // ─── Land / Other ───
  { name: "Non-Crop Land / Bunds", emoji: "🌾" },
];

const PUMP_PRESETS = [
  { label: "25 l", value: 25 },
  { label: "20 l", value: 20 },
  { label: "16 l", value: 16 },
  { label: "15 l", value: 15 },
  { label: "12 l", value: 12 },
  { label: "10 l", value: 10 },
  { label: "Other / Custom", value: -1 },
];

export interface RecentCalculation {
  id: string;
  timestamp: number;
  crop: string;
  cropEmoji: string;
  totalProduct: number;
  totalProductUnit: string;
  dosePerRefill: number;
  pumpRefills: number;
  area: number;
  areaUnit: string;
  productDosage: number;
  dosageUnit: string;
  waterAmount: number;
  waterUnit: string;
  pumpSize: number;
}

export default function PesticideCalculator() {
  const [selectedCrop, setSelectedCrop] = React.useState<CropOption>(CROPS[0]);
  const [isCropDropdownOpen, setIsCropDropdownOpen] = React.useState(false);
  const [cropDropdownSearch, setCropDropdownSearch] = React.useState("");

  // Filter crops in the select dropdown by search query
  const filteredDropdownCrops = React.useMemo(() => {
    if (!cropDropdownSearch.trim()) return CROPS;
    const q = cropDropdownSearch.toLowerCase();
    return CROPS.filter((c) => c.name.toLowerCase().includes(q));
  }, [cropDropdownSearch]);

  // Pre-load user's farm profile crops on initial mount
  React.useEffect(() => {
    try {
      const dataEl = document.getElementById("user-crops-data");
      if (dataEl && dataEl.textContent) {
        const userCrops: string[] = JSON.parse(dataEl.textContent);
        if (Array.isArray(userCrops) && userCrops.length > 0) {
          const first = userCrops[0];
          const matched = CROPS.find(
            (c) =>
              c.name.toLowerCase() === first.toLowerCase() ||
              first.toLowerCase().includes(c.name.toLowerCase()) ||
              c.name.toLowerCase().includes(first.toLowerCase())
          );
          if (matched) {
            setSelectedCrop(matched);
          }
        }
      }
    } catch {
      // Ignore if element is not present or invalid
    }
  }, []);

  // Stepper & Area State
  const [area, setArea] = React.useState<number>(1.0);
  const [areaUnit, setAreaUnit] = React.useState<"Acre" | "Hectare" | "Gunta">("Acre");

  // Inputs State
  const [productDosage, setProductDosage] = React.useState<number>(0);
  const [dosageUnit, setDosageUnit] = React.useState<string>("ml/ac");
  const [waterAmount, setWaterAmount] = React.useState<number>(200);
  const [pumpSize, setPumpSize] = React.useState<number>(25);
  const [isCustomPump, setIsCustomPump] = React.useState(false);
  const [customPumpSize, setCustomPumpSize] = React.useState<number>(18);

  // Formulation Search State
  const [searchQuery, setSearchQuery] = React.useState<string>("");
  const [selectedCategoryFilter, setSelectedCategoryFilter] = React.useState<string>("All");
  const [isSearching, setIsSearching] = React.useState(false);
  const searchContainerRef = React.useRef<HTMLDivElement>(null);

  // Close search dropdown on outside click or Escape key
  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent | TouchEvent) {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(event.target as Node)
      ) {
        setIsSearching(false);
      }
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsSearching(false);
      }
    }

    if (isSearching) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("touchstart", handleClickOutside);
      document.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("touchstart", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isSearching]);

  // Active Spray / Formulation Card State (Screenshot 1, 2, 3)
  const [activeFormulation, setActiveFormulation] = React.useState<PesticideFormulation | null>(null);
  const [formulationCrop, setFormulationCrop] = React.useState<FormulationCropUse | null>(null);
  const [formulationDisease, setFormulationDisease] = React.useState<FormulationDiseaseTarget | null>(null);

  // Modals
  const [showCropModal, setShowCropModal] = React.useState(false);
  const [cropSearchQuery, setCropSearchQuery] = React.useState("");
  const [showDiseaseModal, setShowDiseaseModal] = React.useState(false);
  const [pendingSelectedDisease, setPendingSelectedDisease] = React.useState<{
    crop: FormulationCropUse;
    disease: FormulationDiseaseTarget;
  } | null>(null);

  const [showDetailsModal, setShowDetailsModal] = React.useState(false);
  const [showMeasureModal, setShowMeasureModal] = React.useState(false);

  // Info Tooltip Popovers ("dosage" | "water" | null)
  const [activeTooltip, setActiveTooltip] = React.useState<"dosage" | "water" | null>(null);

  // Audio Speech
  const [isSpeaking, setIsSpeaking] = React.useState(false);
  const [justCalculated, setJustCalculated] = React.useState(false);
  const [validationError, setValidationError] = React.useState<string | null>(null);

  const [lastCalculationSnapshot, setLastCalculationSnapshot] = React.useState<{
    area: number;
    areaUnit: string;
    productDosage: number;
    dosageUnit: string;
    waterAmount: number;
    pumpSize: number;
    totalProduct: number;
    dosePerRefill: number;
    pumpRefills: number;
    baseProductUnit: string;
  } | null>(null);

  // Calculated result to display in top summary cards (shows result after Calculate, but blank on refresh)
  const [displayedResult, setDisplayedResult] = React.useState<{
    totalProduct: number;
    dosePerRefill: number;
    pumpRefills: number;
    baseProductUnit: string;
  } | null>(null);

  // Recent Calculations
  const [recentCalcs, setRecentCalcs] = React.useState<RecentCalculation[]>(() => {
    try {
      const saved = localStorage.getItem("km_recent_pesticide_calcs");
      if (saved) return JSON.parse(saved);
    } catch {
      // fallback
    }
    return [
      {
        id: "sample-1",
        timestamp: Date.now() - 3600000,
        crop: "Tomato",
        cropEmoji: "🍅",
        totalProduct: 50,
        totalProductUnit: "ml",
        dosePerRefill: 6,
        pumpRefills: 8,
        area: 1,
        areaUnit: "ac",
        productDosage: 50,
        dosageUnit: "ml/ac",
        waterAmount: 200,
        waterUnit: "l/ac",
        pumpSize: 25,
      },
    ];
  });

  // Keep localStorage synchronized
  React.useEffect(() => {
    try {
      localStorage.setItem("km_recent_pesticide_calcs", JSON.stringify(recentCalcs));
    } catch {
      // ignore
    }
  }, [recentCalcs]);

  // Derived unit labels & effective pump size
  const isLiquid = dosageUnit.startsWith("ml");
  const baseProductUnit = isLiquid ? "ml" : "g";
  const effectivePumpSize = isCustomPump ? (customPumpSize > 0 ? customPumpSize : 25) : pumpSize > 0 ? pumpSize : 25;

  // Calculation Logic (strictly matching Screenshot 3 formulas)
  const normalizedAreaInDoseUnit = React.useMemo(() => {
    if (dosageUnit.endsWith("/ac")) {
      if (areaUnit === "Acre") return area;
      if (areaUnit === "Hectare") return area * 2.471;
      if (areaUnit === "Gunta") return area / 40.0;
    } else if (dosageUnit.endsWith("/ha")) {
      if (areaUnit === "Hectare") return area;
      if (areaUnit === "Acre") return area / 2.471;
      if (areaUnit === "Gunta") return area / 98.84;
    } else if (dosageUnit.endsWith("/gunta")) {
      if (areaUnit === "Gunta") return area;
      if (areaUnit === "Acre") return area * 40.0;
      if (areaUnit === "Hectare") return area * 98.84;
    }
    return area;
  }, [area, areaUnit, dosageUnit]);

  // Total Product = Area to treat × Product dosage
  const totalProductExact = Math.max(0, normalizedAreaInDoseUnit * productDosage);
  const totalProduct = Math.round(totalProductExact * 10) / 10;

  // Pump Refills = (Water amount ÷ Pump size) × Area to treat
  const refillsExact = effectivePumpSize > 0 ? (waterAmount / effectivePumpSize) * normalizedAreaInDoseUnit : 1;
  const pumpRefills = Math.max(1, Math.round(refillsExact));

  // Dose per refill = Total product ÷ Pump refills
  const dosePerRefillExact = pumpRefills > 0 ? totalProduct / pumpRefills : 0;
  const dosePerRefill = Math.round(dosePerRefillExact);

  // Active calculation result: live calculation while dosage is entered, or the last calculated result, or null (blank on fresh load/refresh)
  const activeResult = productDosage > 0 ? {
    totalProduct,
    dosePerRefill,
    pumpRefills,
    baseProductUnit,
  } : displayedResult;

  // Stepper handlers
  const handleDecrement = () => {
    setArea((prev) => Math.max(0.1, Math.round((prev - 0.5) * 10) / 10));
  };

  const handleIncrement = () => {
    setArea((prev) => Math.round((prev + 0.5) * 10) / 10);
  };

  // Perform calculate button click
  const handleCalculate = () => {
    // If dosage is 0 (e.g. form was just reset and user accidentally clicked Calculate again), do not save duplicate
    if (productDosage <= 0) {
      setValidationError("Please enter product dosage or choose a formulation first.");
      setTimeout(() => setValidationError(null), 3000);
      return;
    }

    if (waterAmount <= 0) {
      setValidationError("Please enter water amount.");
      setTimeout(() => setValidationError(null), 3000);
      return;
    }

    if (area <= 0) {
      setValidationError("Please enter a valid area.");
      setTimeout(() => setValidationError(null), 3000);
      return;
    }

    // Check if duplicate of the most recent calculation
    const isDuplicateOfLatest = recentCalcs.length > 0 &&
      recentCalcs[0].crop === selectedCrop.name &&
      recentCalcs[0].productDosage === productDosage &&
      recentCalcs[0].dosageUnit === dosageUnit &&
      recentCalcs[0].waterAmount === waterAmount &&
      recentCalcs[0].area === area &&
      recentCalcs[0].pumpSize === effectivePumpSize;

    if (isDuplicateOfLatest) {
      setValidationError("This calculation is already saved in recent calculations.");
      setTimeout(() => setValidationError(null), 3000);
      return;
    }

    setValidationError(null);

    const newEntry: RecentCalculation = {
      id: "calc-" + Date.now(),
      timestamp: Date.now(),
      crop: selectedCrop.name,
      cropEmoji: selectedCrop.emoji,
      totalProduct,
      totalProductUnit: baseProductUnit,
      dosePerRefill,
      pumpRefills,
      area,
      areaUnit: areaUnit === "Acre" ? "ac" : areaUnit === "Hectare" ? "ha" : "gunta",
      productDosage,
      dosageUnit,
      waterAmount,
      waterUnit: dosageUnit.endsWith("/ha") ? "l/ha" : "l/ac",
      pumpSize: effectivePumpSize,
    };
    setRecentCalcs((prev) => [newEntry, ...prev.filter((p) => p.id !== newEntry.id)].slice(0, 10));

    setLastCalculationSnapshot({
      area,
      areaUnit,
      productDosage,
      dosageUnit,
      waterAmount,
      pumpSize: effectivePumpSize,
      totalProduct,
      dosePerRefill,
      pumpRefills,
      baseProductUnit,
    });

    // Store calculated result so top summary cards show the result after inputs are reset
    setDisplayedResult({
      totalProduct,
      dosePerRefill,
      pumpRefills,
      baseProductUnit,
    });

    // Reset input fields as explicitly requested by user
    setProductDosage(0);
    setWaterAmount(200);
    setArea(1.0);
    setActiveFormulation(null);
    setFormulationCrop(null);
    setFormulationDisease(null);
    setSearchQuery("");
    setIsSearching(false);
    setIsCustomPump(false);
    setPumpSize(25);
    setCustomPumpSize(25);
    setActiveTooltip(null);

    setJustCalculated(true);
    setTimeout(() => setJustCalculated(false), 3000);

    if (typeof window !== "undefined" && window.navigator && window.navigator.vibrate) {
      window.navigator.vibrate(30);
    }
  };

  // Restore calculation from recent card
  const handleRestore = (item: RecentCalculation) => {
    const matchedCrop = CROPS.find((c) => c.name === item.crop) || { name: item.crop, emoji: item.cropEmoji };
    setSelectedCrop(matchedCrop);
    setArea(item.area);
    setAreaUnit(item.areaUnit === "ac" ? "Acre" : item.areaUnit === "ha" ? "Hectare" : "Gunta");
    setProductDosage(item.productDosage);
    setDosageUnit(item.dosageUnit);
    setWaterAmount(item.waterAmount);
    if (PUMP_PRESETS.some((p) => p.value === item.pumpSize)) {
      setIsCustomPump(false);
      setPumpSize(item.pumpSize);
    } else {
      setIsCustomPump(true);
      setCustomPumpSize(item.pumpSize);
    }
    setLastCalculationSnapshot({
      area: item.area,
      areaUnit: item.areaUnit === "ac" ? "Acre" : item.areaUnit === "ha" ? "Hectare" : "Gunta",
      productDosage: item.productDosage,
      dosageUnit: item.dosageUnit,
      waterAmount: item.waterAmount,
      pumpSize: item.pumpSize,
      totalProduct: item.totalProduct,
      dosePerRefill: item.dosePerRefill,
      pumpRefills: item.pumpRefills,
      baseProductUnit: item.totalProductUnit,
    });
    setDisplayedResult({
      totalProduct: item.totalProduct,
      dosePerRefill: item.dosePerRefill,
      pumpRefills: item.pumpRefills,
      baseProductUnit: item.totalProductUnit,
    });
    setValidationError(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Delete calculation from recent list
  const handleDeleteRecent = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setRecentCalcs((prev) => prev.filter((p) => p.id !== id));
  };

  // Audio Speech Synthesis for Listen Button
  const handleListen = () => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    window.speechSynthesis.cancel();
    const snap = lastCalculationSnapshot || (productDosage > 0 ? {
      area,
      areaUnit: areaUnit === "Acre" ? "ac" : areaUnit === "Hectare" ? "ha" : "gunta",
      productDosage,
      dosageUnit,
      waterAmount,
      pumpSize: effectivePumpSize,
      totalProduct,
      dosePerRefill,
      pumpRefills,
      baseProductUnit,
    } : null);

    if (!snap) {
      const spokenText = "Please enter product dosage or choose a formulation to calculate.";
      const utterance = new SpeechSynthesisUtterance(spokenText);
      utterance.rate = 0.95;
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      setIsSpeaking(true);
      window.speechSynthesis.speak(utterance);
      return;
    }

    const spokenText = `For ${snap.area} ${snap.areaUnit}, use a total of ${snap.totalProduct} ${snap.baseProductUnit} of product. For your ${snap.pumpSize} litre pump, use ${snap.dosePerRefill} ${snap.baseProductUnit} per refill. Refill your pump ${snap.pumpRefills} times to treat the full area.`;
    const utterance = new SpeechSynthesisUtterance(spokenText);
    utterance.rate = 0.95;
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  // Filtered formulation presets
  const filteredFormulations = React.useMemo(() => {
    return PESTICIDES_DATABASE.filter((item) => {
      if (selectedCategoryFilter !== "All" && item.category !== selectedCategoryFilter) {
        return false;
      }
      if (!searchQuery.trim()) return true;

      const q = searchQuery.toLowerCase();
      const matchName = item.name.toLowerCase().includes(q);
      const matchBrand = item.popularBrand.toLowerCase().includes(q);
      const matchCategory = item.category.toLowerCase().includes(q);
      const matchCrops = item.crops.some((c) =>
        c.cropName.toLowerCase().includes(q) ||
        c.diseases.some((d) => d.name.toLowerCase().includes(q))
      );
      return matchName || matchBrand || matchCategory || matchCrops;
    });
  }, [searchQuery, selectedCategoryFilter]);

  // When user clicks a formulation in the list
  const handleSelectFormulation = (formulation: PesticideFormulation) => {
    setActiveFormulation(formulation);
    setIsSearching(false);
    setSearchQuery("");

    // Look for currently selected crop in this formulation's registered crops
    const currentCropName = selectedCrop.name.toLowerCase();
    const matchedCrop = formulation.crops.find((c) =>
      c.cropName.toLowerCase() === currentCropName ||
      currentCropName.includes(c.cropName.toLowerCase()) ||
      c.cropName.toLowerCase().includes(currentCropName)
    );

    if (matchedCrop) {
      setFormulationCrop(matchedCrop);
      if (matchedCrop.diseases.length > 0) {
        const firstDisease = matchedCrop.diseases[0];
        setFormulationDisease(firstDisease);
        setProductDosage(firstDisease.dosage);
        setDosageUnit(firstDisease.dosageUnit);
        setWaterAmount(firstDisease.waterAmount);
      } else {
        setFormulationDisease(null);
      }
    } else {
      if (formulation.crops.length > 0) {
        const firstCrop = formulation.crops[0];
        setFormulationCrop(firstCrop);
        if (firstCrop.diseases.length > 0) {
          const firstDisease = firstCrop.diseases[0];
          setFormulationDisease(firstDisease);
          setProductDosage(firstDisease.dosage);
          setDosageUnit(firstDisease.dosageUnit);
          setWaterAmount(firstDisease.waterAmount);
          const matchingGlobalCrop = CROPS.find((c) => c.name.toLowerCase() === firstCrop.cropName.toLowerCase());
          if (matchingGlobalCrop) setSelectedCrop(matchingGlobalCrop);
        }
      } else {
        setFormulationCrop(null);
        setFormulationDisease(null);
      }
    }
  };

  return (
    <div className="pesticide-calc-page w-full max-w-md mx-auto pb-16 font-sans select-none sm:select-auto">
      {/* Top Header */}
      <div className="flex items-center justify-between py-3 mb-2">
        <button
          type="button"
          onClick={() => {
            if (typeof window !== "undefined") {
              if (window.history.length > 1) {
                window.history.back();
              } else {
                window.location.href = "/";
              }
            }
          }}
          className="btn-21st btn-21st-secondary h-10 w-10 !rounded-full p-0 flex items-center justify-center shadow-xs active:scale-95 transition-all cursor-pointer"
          aria-label="Back"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>

        <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
          Pesticide calculator
        </h1>

        <div className="w-10" />
      </div>

      {/* Subheader: "Per application" + Crop Picker Pill */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-semibold text-slate-900 dark:text-white">
          Per application
        </span>

        {/* Crop Selector Pill */}
        <div className="relative">
          <button
            type="button"
            onClick={() => {
              setIsCropDropdownOpen(!isCropDropdownOpen);
              setCropDropdownSearch("");
            }}
            className="btn-21st btn-21st-secondary btn-21st-pill btn-21st-xs formulation-pill"
          >
            <span>{selectedCrop.emoji}</span>
            <span>{selectedCrop.name}</span>
            <ChevronDown className="h-3.5 w-3.5 opacity-70 shrink-0" />
          </button>

          {isCropDropdownOpen && (
            <>
              <div
                className="fixed inset-0 z-30"
                onClick={() => setIsCropDropdownOpen(false)}
              />
              <div className="absolute right-0 top-full mt-1.5 z-40 w-60 rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900 max-h-80 overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
                {/* Search inside crop dropdown */}
                <div className="p-2 border-b border-slate-100 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-800/80">
                  <div className="relative flex items-center">
                    <Search className="absolute left-2.5 h-3.5 w-3.5 text-slate-400 pointer-events-none" />
                    <input
                      type="text"
                      placeholder="Search crop…"
                      value={cropDropdownSearch}
                      onChange={(e) => setCropDropdownSearch(e.target.value)}
                      className="w-full rounded-xl border border-slate-200 bg-white py-1.5 pl-8 pr-2 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                      autoFocus
                    />
                  </div>
                </div>

                <div className="overflow-y-auto max-h-64 py-1 divide-y divide-slate-100/40 dark:divide-slate-800/40">
                  {filteredDropdownCrops.length === 0 ? (
                    <div className="p-4 text-center text-xs text-slate-400">
                      No crop found
                    </div>
                  ) : (
                    filteredDropdownCrops.map((crop) => (
                      <button
                        key={crop.name}
                        type="button"
                        onClick={() => {
                          setSelectedCrop(crop);
                          setIsCropDropdownOpen(false);
                          setCropDropdownSearch("");
                          if (activeFormulation) {
                            const m = activeFormulation.crops.find((c) =>
                              c.cropName.toLowerCase() === crop.name.toLowerCase() ||
                              c.cropName.toLowerCase().includes(crop.name.toLowerCase()) ||
                              crop.name.toLowerCase().includes(c.cropName.toLowerCase())
                            );
                            if (m) {
                              setFormulationCrop(m);
                              if (m.diseases.length > 0) {
                                setFormulationDisease(m.diseases[0]);
                                setProductDosage(m.diseases[0].dosage);
                                setDosageUnit(m.diseases[0].dosageUnit);
                                setWaterAmount(m.diseases[0].waterAmount);
                              }
                            }
                          }
                        }}
                        className={`flex w-full items-center gap-2.5 px-3.5 py-2 text-left text-xs font-medium transition-colors cursor-pointer ${
                          selectedCrop.name === crop.name
                            ? "bg-blue-50 text-blue-700 dark:bg-blue-950/80 dark:text-blue-300 font-semibold"
                            : "text-slate-700 hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-slate-800"
                        }`}
                      >
                        <span className="text-base">{crop.emoji}</span>
                        <span className="flex-1 truncate">{crop.name}</span>
                        {selectedCrop.name === crop.name && (
                          <Check className="h-3.5 w-3.5 text-blue-600 dark:text-blue-400 shrink-0" />
                        )}
                      </button>
                    ))
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Listen Audio Button */}
      <div className="mb-4">
        <button
          type="button"
          onClick={handleListen}
          className={`btn-21st btn-21st-pill btn-21st-sm inline-flex items-center gap-2 font-bold px-3.5 py-1.5 shadow-2xs active:scale-95 transition-all cursor-pointer ${
            isSpeaking ? "bg-red-500 text-white border-red-600 dark:bg-red-600" : "btn-21st-secondary"
          }`}
        >
          {isSpeaking ? (
            <>
              <VolumeX className="h-4 w-4 animate-pulse text-white" />
              <span>Stop listening</span>
            </>
          ) : (
            <>
              <Volume2 className="h-4 w-4 text-blue-600 dark:text-sky-400" />
              <span>Listen</span>
            </>
          )}
        </button>
      </div>

      {/* Top Results Display Cards (Soft blue/lavender tint matching reference screenshot) */}
      <div className="space-y-3 mb-3">
        {/* Hero Card: Total Product */}
        <div className="rounded-[22px] bg-[#eef4ff] border border-blue-100 p-6 text-center dark:bg-[#152347] dark:border-blue-900/60 shadow-xs">
          <p className="text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1.5">
            Total product
          </p>
          <div className="flex items-baseline justify-center gap-1.5">
            <span className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              {activeResult ? activeResult.totalProduct : "---"}
            </span>
            <span className="text-lg font-bold text-slate-700 dark:text-slate-200">
              {activeResult ? activeResult.baseProductUnit : baseProductUnit}
            </span>
          </div>
        </div>

        {/* Row of 2 Cards: Dose per refill & Pump refills */}
        <div className="grid grid-cols-2 gap-3">
          {/* Dose per refill */}
          <div className="rounded-[22px] bg-[#eef4ff] border border-blue-100 p-4 dark:bg-[#152347] dark:border-blue-900/60 shadow-xs flex flex-col justify-between">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/95 text-blue-700 shadow-2xs dark:bg-slate-800 dark:text-blue-400 mb-3">
              <Droplet className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-[11px] font-semibold text-slate-600 dark:text-slate-300">
                Dose per refill
              </p>
              <p className="text-lg font-extrabold text-slate-900 dark:text-white">
                {activeResult ? `${activeResult.dosePerRefill} ${activeResult.baseProductUnit}` : `--- ${baseProductUnit}`}
              </p>
            </div>
          </div>

          {/* Pump refills */}
          <div className="rounded-[22px] bg-[#eef4ff] border border-blue-100 p-4 dark:bg-[#152347] dark:border-blue-900/60 shadow-xs flex flex-col justify-between">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/95 text-blue-700 shadow-2xs dark:bg-slate-800 dark:text-blue-400 mb-3">
              <RefreshCw className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-[11px] font-semibold text-slate-600 dark:text-slate-300">
                Pump refills
              </p>
              <p className="text-lg font-extrabold text-slate-900 dark:text-white">
                {activeResult ? `${activeResult.pumpRefills} times` : "--- times"}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Calculation Details Button */}
      <div className="text-center mb-6">
        <button
          type="button"
          onClick={() => setShowDetailsModal(true)}
          className="btn-21st btn-21st-secondary btn-21st-pill btn-21st-xs inline-flex items-center gap-1.5 font-bold px-3.5 py-1.5 shadow-2xs active:scale-95 transition-all cursor-pointer"
        >
          <Calculator className="h-3.5 w-3.5 text-blue-600 dark:text-sky-400" />
          <span>Calculation details</span>
        </button>
      </div>

      {/* Section: Area to treat */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-bold text-slate-900 dark:text-white">
            Area to treat
          </span>
          <button
            type="button"
            onClick={() => setShowMeasureModal(true)}
            className="btn-21st btn-21st-secondary btn-21st-pill btn-21st-xs inline-flex items-center gap-1.5 font-bold px-3 py-1 shadow-2xs active:scale-95 transition-all cursor-pointer"
          >
            <Ruler className="h-3.5 w-3.5 text-blue-600 dark:text-sky-400" />
            <span>Measure</span>
          </button>
        </div>

        {/* Stepper Input: [-] [ 1.0 Acre ] [+] */}
        <div className="flex items-center justify-between gap-3 mb-3">
          <button
            type="button"
            onClick={handleDecrement}
            className="btn-21st stepper-btn flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl active:scale-95 transition-all cursor-pointer"
            aria-label="Decrease area"
          >
            <Minus className="h-6 w-6 stroke-[2.5]" />
          </button>

          <div className="area-stepper-box flex-1 flex flex-col items-center justify-center rounded-2xl py-2.5 px-4 bg-[#f5f6f9] dark:bg-[#18233c] border border-slate-200/80 dark:border-slate-700">
            <input
              type="number"
              step="0.1"
              min="0.1"
              value={area}
              onChange={(e) => setArea(parseFloat(e.target.value) || 0.1)}
              className="area-stepper-input w-full text-center text-3xl font-extrabold text-slate-900 dark:text-white bg-transparent outline-none focus:ring-0 border-0 p-0"
            />
            <span className="area-stepper-unit text-xs font-semibold text-slate-500 dark:text-slate-300">
              {areaUnit}
            </span>
          </div>

          <button
            type="button"
            onClick={handleIncrement}
            className="btn-21st stepper-btn flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl active:scale-95 transition-all cursor-pointer"
            aria-label="Increase area"
          >
            <Plus className="h-6 w-6 stroke-[2.5]" />
          </button>
        </div>

        {/* Radio Buttons for Area unit: Acre / Hectare / Gunta */}
        <div className="flex items-center gap-6 pt-1">
          {(["Acre", "Hectare", "Gunta"] as const).map((unit) => (
            <label
              key={unit}
              className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-800 dark:text-white"
            >
              <input
                type="radio"
                name="areaUnit"
                value={unit}
                checked={areaUnit === unit}
                onChange={() => setAreaUnit(unit)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-300 dark:border-slate-600"
              />
              <span>{unit}</span>
            </label>
          ))}
        </div>
      </div>

      <hr className="border-slate-200 dark:border-slate-800 my-6" />

      {/* Selected Spray / Formulation Card (Screenshot 1 & 2 Fix) */}
      {activeFormulation && (
        <div className="formulation-card rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-[#f8f9fc] dark:bg-[#111c33] p-4 sm:p-5 mb-6 shadow-xs relative">
          {/* Close Button */}
          <button
            type="button"
            onClick={() => {
              setActiveFormulation(null);
              setFormulationCrop(null);
              setFormulationDisease(null);
            }}
            className="formulation-close-btn absolute right-3.5 top-3.5 inline-flex items-center justify-center h-7 w-7 rounded-full text-slate-400 hover:text-red-500 bg-white hover:bg-red-50 dark:bg-slate-800 dark:hover:bg-red-950/50 border border-slate-200 dark:border-slate-700 shadow-2xs transition-all cursor-pointer active:scale-90"
            title="Remove formulation"
            aria-label="Remove formulation"
          >
            <X className="h-4 w-4" />
          </button>

          {/* Formulation Header */}
          <div className="flex items-center gap-3 mb-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-50 text-blue-700 dark:bg-slate-800 dark:text-blue-400">
              <Droplet className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="pr-8">
              <span className="inline-block text-[11px] font-bold text-blue-600 dark:text-sky-400 uppercase tracking-wider">
                {activeFormulation.category}
              </span>
              <h3 className="text-base font-extrabold text-slate-900 dark:text-white leading-tight">
                {activeFormulation.name}
              </h3>
              {activeFormulation.popularBrand && (
                <span className="text-xs text-slate-500 dark:text-slate-300 font-medium">
                  {activeFormulation.popularBrand}
                </span>
              )}
            </div>
          </div>

          <hr className="border-slate-200/70 dark:border-slate-800 my-3" />

          {/* 21st dev Pill Dropdowns: [ 🥔 Potato ⌄ ] [ Early & Late Blight ⌄ ] */}
          <div className="flex items-center gap-2 mb-3.5 flex-wrap">
            <button
              type="button"
              onClick={() => {
                setCropSearchQuery("");
                setShowCropModal(true);
              }}
              className="btn-21st btn-21st-secondary btn-21st-pill btn-21st-sm formulation-pill"
            >
              <span>{formulationCrop ? `${formulationCrop.cropEmoji} ${formulationCrop.cropName}` : "Select crop"}</span>
              <ChevronDown className="h-3.5 w-3.5 opacity-70 shrink-0" />
            </button>

            <button
              type="button"
              onClick={() => {
                if (formulationCrop) {
                  setPendingSelectedDisease(
                    formulationDisease ? { crop: formulationCrop, disease: formulationDisease } : null
                  );
                  setShowDiseaseModal(true);
                } else {
                  setShowCropModal(true);
                }
              }}
              className="btn-21st btn-21st-secondary btn-21st-pill btn-21st-sm formulation-pill max-w-[220px]"
            >
              <span className="truncate">{formulationDisease ? formulationDisease.name : "Select disease"}</span>
              <ChevronDown className="h-3.5 w-3.5 opacity-70 shrink-0" />
            </button>
          </div>

          {/* Info callout */}
          <div className="formulation-info-box rounded-xl bg-slate-100 dark:bg-slate-800 p-3 mb-3.5 flex items-start gap-2 text-xs text-slate-700 dark:text-slate-200">
            <Info className="h-4 w-4 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
            <span>
              {formulationCrop && formulationDisease
                ? `Standard dosage for ${formulationDisease.name} in ${formulationCrop.cropName}`
                : "Select a crop and disease to get the product dosage and water amount"}
            </span>
          </div>

          {/* Dosage & Water summary */}
          <div className="space-y-2 text-xs">
            <div>
              <span className="block text-slate-500 dark:text-slate-400 text-[11px] font-medium">Product dosage</span>
              <span className="font-extrabold text-slate-900 dark:text-white text-sm">
                {formulationDisease ? `${formulationDisease.dosage} ${formulationDisease.dosageUnit}` : "---"}
              </span>
            </div>
            <div>
              <span className="block text-slate-500 dark:text-slate-400 text-[11px] font-medium">Water amount</span>
              <span className="font-extrabold text-slate-900 dark:text-white text-sm">
                {formulationDisease ? `${formulationDisease.waterAmount} ${formulationDisease.waterUnit}` : "---"}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Card: Don't know dosage? (Extensive database lookup) */}
      <div className="rounded-2xl bg-[#f5f6f9] dark:bg-[#111c33] border border-slate-200/80 dark:border-slate-700/80 p-4 mb-6">
        <h3 className="text-base font-extrabold text-slate-900 dark:text-white mb-0.5">
          Don't know dosage?
        </h3>
        <p className="text-xs text-slate-600 dark:text-slate-300 mb-3">
          Search by formulation, crop and disease instead
        </p>

        {/* 21st dev Category Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2.5 mb-2 no-scrollbar">
          {["All", "Insecticide", "Fungicide", "Bactericide", "Virucide", "Herbicide", "Acaricide", "Nematicide", "Bio-pesticide"].map(
            (cat) => {
              const isActive = selectedCategoryFilter === cat;
              return (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCategoryFilter(cat)}
                  className={`btn-21st btn-21st-pill btn-21st-xs whitespace-nowrap cat-filter-pill ${
                    isActive ? "btn-21st-primary is-active" : "btn-21st-secondary"
                  }`}
                >
                  {cat}
                </button>
              );
            }
          )}
        </div>

        <div ref={searchContainerRef} className="relative z-30">
          <div className="relative flex items-center">
            <Search className="absolute left-3.5 h-4 w-4 text-slate-400 pointer-events-none" />
            <input
              type="text"
              placeholder="Search formulation, pest, fungus, or weed…"
              value={searchQuery}
              onFocus={() => setIsSearching(true)}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setIsSearching(true);
              }}
              className="w-full rounded-full border border-slate-200 bg-white py-2.5 pl-10 pr-9 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-white"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="absolute right-3 p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                aria-label="Clear search"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>

          {/* Invisible backdrop to dismiss dropdown on click outside */}
          {isSearching && (
            <div
              className="fixed inset-0 z-20 cursor-default bg-transparent"
              onClick={() => setIsSearching(false)}
              aria-hidden="true"
            />
          )}

          {isSearching && (
            <div className="absolute left-0 right-0 top-full mt-2 z-30 rounded-2xl border border-slate-200/90 bg-white/95 dark:bg-[#111c33]/95 backdrop-blur-md p-2 shadow-2xl dark:border-slate-700 max-h-80 overflow-y-auto animate-in fade-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between px-2.5 pb-2 pt-1 border-b border-slate-100 dark:border-slate-800 text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                <span>Database ({filteredFormulations.length} formulations)</span>
                <button
                  type="button"
                  onClick={() => setIsSearching(false)}
                  className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 text-xs font-bold"
                >
                  Close
                </button>
              </div>

              {filteredFormulations.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-500 dark:text-slate-400">
                  No formulations matching your search.
                </div>
              ) : (
                filteredFormulations.map((f) => (
                  <button
                    key={f.id}
                    type="button"
                    onClick={() => handleSelectFormulation(f)}
                    className="flex w-full flex-col rounded-xl px-2.5 py-2 text-left hover:bg-blue-50 dark:hover:bg-slate-800/80 transition-colors border-b border-slate-100 dark:border-slate-800/50 last:border-0 cursor-pointer"
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        {f.name}
                      </span>
                      <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 border border-blue-100 dark:border-blue-900">
                        {f.category}
                      </span>
                    </div>
                    <span className="text-[10px] text-blue-600 dark:text-blue-400 font-semibold mt-0.5">
                      {f.popularBrand}
                    </span>
                    <span className="text-[10px] text-slate-500 dark:text-slate-300 truncate mt-0.5">
                      Crops: {f.crops.map((c) => c.cropName).join(", ")}
                    </span>
                  </button>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* ─── Compact Horizontal Arrangement (matching reference photo) ─── */}

      {/* Row 1: Product dosage */}
      <div className="py-3 border-b border-slate-200/80 dark:border-slate-800">
        <div className="flex items-center justify-between gap-3">
          <div className="pr-2 flex-1">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900 dark:text-white">
              <span className="cursor-default">Product dosage</span>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setActiveTooltip(activeTooltip === "dosage" ? null : "dosage");
                }}
                className={`pesticide-info-trigger ${activeTooltip === "dosage" ? "is-active" : ""}`}
                style={{
                  WebkitAppearance: "none",
                  MozAppearance: "none",
                  appearance: "none",
                  outline: "none",
                  borderStyle: "solid",
                  boxSizing: "border-box",
                }}
                title="Click for dosage instructions"
                aria-label="Click for dosage instructions"
              >
                <Info className="h-3 w-3 stroke-[2.5]" />
              </button>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              Product dosage needed per acre or hectare
            </p>
          </div>

          <div className="flex items-center rounded-2xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 shadow-2xs shrink-0 w-44 justify-between focus-within:border-blue-500 transition-colors">
            <input
              type="number"
              min="0"
              step="1"
              value={productDosage || ""}
              placeholder="0"
              onChange={(e) => setProductDosage(parseFloat(e.target.value) || 0)}
              className="w-16 text-right text-sm font-bold text-slate-900 dark:text-white bg-transparent outline-none border-0 p-0"
            />
            <select
              value={dosageUnit}
              onChange={(e) => setDosageUnit(e.target.value)}
              className="ml-2 bg-transparent text-xs font-bold text-slate-700 dark:text-slate-200 outline-none border-0 cursor-pointer pr-1"
            >
              <option value="ml/ac">ml/ac</option>
              <option value="g/ac">g/ac</option>
              <option value="ml/ha">ml/ha</option>
              <option value="g/ha">g/ha</option>
              <option value="ml/gunta">ml/gunta</option>
              <option value="g/gunta">g/gunta</option>
            </select>
          </div>
        </div>

        {/* Product Dosage Info Tooltip (matches Screenshot 1 & 6) */}
        {activeTooltip === "dosage" && (
          <div
            className="pesticide-info-tooltip relative z-20 mt-3 p-4 rounded-2xl shadow-xl animate-in fade-in slide-in-from-top-2 duration-200"
            style={{ backgroundColor: "#0f172a", color: "#ffffff" }}
          >
            <div
              className="pesticide-info-tooltip-arrow absolute -top-2 right-16 h-0 w-0 border-x-8 border-x-transparent border-b-8"
              style={{ borderBottomColor: "#0f172a" }}
            />
            <div className="flex items-start justify-between gap-3">
              <p
                className="pesticide-tooltip-text text-xs leading-relaxed font-medium pr-1"
                style={{ color: "#ffffff", WebkitTextFillColor: "#ffffff", margin: 0 }}
              >
                The product dosage indicates how much product to use per 1 acre or hectare, typically measured in g or ml per acre or hectare. You can find this information on the product label, usually under “Directions for Use,” or consult an advisor.
              </p>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setActiveTooltip(null);
                }}
                className="pesticide-tooltip-close"
                style={{
                  WebkitAppearance: "none",
                  MozAppearance: "none",
                  appearance: "none",
                  outline: "none",
                  borderStyle: "solid",
                  boxSizing: "border-box",
                }}
                title="Close"
                aria-label="Close tooltip"
              >
                <X className="h-3.5 w-3.5 stroke-[2.5]" style={{ color: "#ffffff" }} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Row 2: Water amount */}
      <div className="py-3 border-b border-slate-200/80 dark:border-slate-800">
        <div className="flex items-center justify-between gap-3">
          <div className="pr-2 flex-1">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900 dark:text-white">
              <span className="cursor-default">Water amount</span>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setActiveTooltip(activeTooltip === "water" ? null : "water");
                }}
                className={`pesticide-info-trigger ${activeTooltip === "water" ? "is-active" : ""}`}
                style={{
                  WebkitAppearance: "none",
                  MozAppearance: "none",
                  appearance: "none",
                  outline: "none",
                  borderStyle: "solid",
                  boxSizing: "border-box",
                }}
                title="Click for water amount instructions"
                aria-label="Click for water amount instructions"
              >
                <Info className="h-3 w-3 stroke-[2.5]" />
              </button>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              Water required to mix with product dosage
            </p>
          </div>

          <div className="flex items-center rounded-2xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 shadow-2xs shrink-0 w-44 justify-between focus-within:border-blue-500 transition-colors">
            <input
              type="number"
              min="10"
              step="10"
              value={waterAmount || ""}
              placeholder="200"
              onChange={(e) => setWaterAmount(parseFloat(e.target.value) || 0)}
              className="w-16 text-right text-sm font-bold text-slate-900 dark:text-white bg-transparent outline-none border-0 p-0"
            />
            <span className="text-xs font-bold text-slate-700 dark:text-slate-200 ml-2">
              {dosageUnit.endsWith("/ha") ? "l/ha" : "l/ac"}
            </span>
          </div>
        </div>

        {/* Water Amount Info Tooltip (matches Screenshot 2 & 10) */}
        {activeTooltip === "water" && (
          <div
            className="pesticide-info-tooltip relative z-20 mt-3 p-4 rounded-2xl shadow-xl animate-in fade-in slide-in-from-top-2 duration-200"
            style={{ backgroundColor: "#0f172a", color: "#ffffff" }}
          >
            <div
              className="pesticide-info-tooltip-arrow absolute -top-2 right-16 h-0 w-0 border-x-8 border-x-transparent border-b-8"
              style={{ borderBottomColor: "#0f172a" }}
            />
            <div className="flex items-start justify-between gap-3">
              <div className="space-y-2 pr-1">
                <h4
                  className="pesticide-tooltip-heading text-sm font-bold"
                  style={{ color: "#ffffff", WebkitTextFillColor: "#ffffff", margin: 0 }}
                >
                  Follow label instructions for water amount
                </h4>
                <p
                  className="pesticide-tooltip-text text-xs leading-relaxed font-medium"
                  style={{ color: "#f8fafc", WebkitTextFillColor: "#f8fafc", margin: 0 }}
                >
                  The water amount in which to apply the product is usually given as an amount per area (1 acre or hectare). This is found on the product label. For example 200 l/ac
                </p>
                <p
                  className="pesticide-tooltip-subtext text-[11px] leading-relaxed"
                  style={{ color: "#cbd5e1", WebkitTextFillColor: "#cbd5e1", margin: 0 }}
                >
                  Using less water can cause plant damage and using more can reduce product effectiveness.
                </p>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setActiveTooltip(null);
                }}
                className="pesticide-tooltip-close"
                style={{
                  WebkitAppearance: "none",
                  MozAppearance: "none",
                  appearance: "none",
                  outline: "none",
                  borderStyle: "solid",
                  boxSizing: "border-box",
                }}
                title="Close"
                aria-label="Close tooltip"
              >
                <X className="h-3.5 w-3.5 stroke-[2.5]" style={{ color: "#ffffff" }} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Row 3: Pump size */}
      <div className="flex items-center justify-between gap-3 py-3 border-b border-slate-200/80 dark:border-slate-800">
        <div className="pr-2 flex-1">
          <label className="block text-xs font-bold text-slate-900 dark:text-white">
            Pump size
          </label>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
            Volume of the pump
          </p>
        </div>

        <div className="shrink-0 w-44">
          <select
            value={isCustomPump ? -1 : pumpSize}
            onChange={(e) => {
              const val = parseInt(e.target.value, 10);
              if (val === -1) {
                setIsCustomPump(true);
              } else {
                setIsCustomPump(false);
                setPumpSize(val);
              }
            }}
            className="w-full rounded-2xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-xs font-bold text-slate-900 dark:text-white shadow-2xs outline-none focus:border-blue-500 cursor-pointer"
          >
            {PUMP_PRESETS.map((preset) => (
              <option key={preset.value} value={preset.value}>
                {preset.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Custom Pump Size input when 'Other / Custom' selected */}
      {isCustomPump && (
        <div className="my-3 rounded-2xl border-2 border-blue-500/80 bg-white dark:bg-slate-900 p-3 shadow-2xs animate-in fade-in duration-200">
          <span className="block text-[11px] font-semibold text-slate-600 dark:text-slate-300 mb-1">
            Custom pump capacity:
          </span>
          <div className="flex items-center gap-2">
            <input
              type="number"
              min="1"
              max="2000"
              step="1"
              value={customPumpSize}
              onChange={(e) => setCustomPumpSize(parseFloat(e.target.value) || 1)}
              placeholder="Enter tank litres (e.g. 18)"
              className="flex-1 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-2 text-sm font-bold text-slate-900 dark:text-white outline-none focus:border-blue-500"
            />
            <span className="text-xs font-bold text-slate-700 dark:text-slate-200 px-2">
              Litres
            </span>
          </div>
          <div className="flex items-center gap-1.5 mt-2.5 overflow-x-auto pb-1 no-scrollbar">
            {[5, 8, 14, 18, 50, 100, 200, 500].map((liters) => (
              <button
                key={liters}
                type="button"
                onClick={() => setCustomPumpSize(liters)}
                className={`btn-21st btn-21st-pill btn-21st-xs ${
                  customPumpSize === liters ? "btn-21st-primary is-active" : "btn-21st-secondary"
                }`}
              >
                {liters} L
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 21st.dev Premium Calculate CTA Button */}
      <div className="mb-8">
        <button
          type="button"
          onClick={handleCalculate}
          className={`btn-21st btn-21st-primary btn-21st-pill w-full py-4 text-base font-extrabold shadow-xl tracking-wide flex items-center justify-center gap-2 active:scale-98 transition-all cursor-pointer ${
            productDosage <= 0 ? "opacity-90 hover:opacity-100" : ""
          }`}
        >
          <Sparkles className="h-5 w-5" />
          <span>Calculate</span>
        </button>

        {validationError && (
          <div className="flex items-center justify-center gap-1.5 text-xs font-semibold text-amber-600 dark:text-amber-400 mt-2.5 animate-in fade-in slide-in-from-top-1 duration-200 text-center px-2">
            <Info className="h-4 w-4 shrink-0" />
            <span>{validationError}</span>
          </div>
        )}

        {justCalculated && !validationError && (
          <div className="flex items-center justify-center gap-1.5 text-xs font-bold text-emerald-600 dark:text-emerald-400 mt-2.5 animate-in fade-in slide-in-from-top-1 duration-200 text-center px-2">
            <Check className="h-4 w-4 shrink-0" />
            <span>Calculated! Saved to recent &amp; inputs reset.</span>
          </div>
        )}
      </div>

      {/* Recent Calculations Section (Screenshot 2) */}
      <div>
        <h2 className="text-base font-bold text-slate-900 dark:text-white mb-3">
          Recent calculations
        </h2>

        {recentCalcs.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No recent calculations yet.</p>
        ) : (
          <div className="space-y-3">
            {recentCalcs.map((item) => (
              <div
                key={item.id}
                onClick={() => handleRestore(item)}
                className="pesticide-recent-card group relative cursor-pointer rounded-2xl p-4 bg-white dark:bg-[#131d33] border border-slate-200 dark:border-slate-800 shadow-xs hover:shadow-md transition-all"
              >
                {/* Header: Crop and Trash Icon */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{item.cropEmoji}</span>
                    <span className="text-sm font-extrabold text-slate-900 dark:text-white">
                      {item.crop}
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={(e) => handleDeleteRecent(item.id, e)}
                    className="pesticide-recent-delete-btn h-8 w-8 rounded-xl p-0 flex items-center justify-center text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/40 border border-slate-200 dark:border-slate-700/80 active:scale-95 transition-all cursor-pointer"
                    title="Delete record"
                    aria-label="Delete record"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>

                {/* Grid 1: Total product, Dose per refill, Pump refills */}
                <div className="grid grid-cols-3 gap-2 border-b border-slate-200/80 dark:border-slate-800 pb-3 mb-2.5">
                  <div>
                    <span className="block text-xs font-semibold text-slate-500 dark:text-slate-400">
                      Total product
                    </span>
                    <span className="text-sm font-extrabold text-slate-900 dark:text-white block mt-0.5">
                      {item.totalProduct} {item.totalProductUnit}
                    </span>
                  </div>
                  <div>
                    <span className="block text-xs font-semibold text-slate-500 dark:text-slate-400">
                      Dose per refill
                    </span>
                    <span className="text-sm font-extrabold text-slate-900 dark:text-white block mt-0.5">
                      {item.dosePerRefill} {item.totalProductUnit}
                    </span>
                  </div>
                  <div>
                    <span className="block text-xs font-semibold text-slate-500 dark:text-slate-400">
                      Pump refills
                    </span>
                    <span className="text-sm font-extrabold text-slate-900 dark:text-white block mt-0.5">
                      {item.pumpRefills} times
                    </span>
                  </div>
                </div>

                {/* Grid 2: Area to treat, Product dosage, Water amount, Pump size */}
                <div className="grid grid-cols-4 gap-1 text-[11px]">
                  <div>
                    <span className="block font-medium text-slate-500 dark:text-slate-400">Area to treat</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
                      {item.area} {item.areaUnit}
                    </span>
                  </div>
                  <div>
                    <span className="block font-medium text-slate-500 dark:text-slate-400">Product dosage</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
                      {item.productDosage} {item.dosageUnit}
                    </span>
                  </div>
                  <div>
                    <span className="block font-medium text-slate-500 dark:text-slate-400">Water amount</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
                      {item.waterAmount} {item.waterUnit}
                    </span>
                  </div>
                  <div>
                    <span className="block font-medium text-slate-500 dark:text-slate-400">Pump size</span>
                    <span className="font-bold text-slate-800 dark:text-slate-200 block mt-0.5">
                      {item.pumpSize} l
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ─── MODAL: Select your crop (Screenshot 2) ─── */}
      {showCropModal && activeFormulation && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/70 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="modal-dialog-box relative w-full max-w-sm rounded-t-3xl sm:rounded-3xl bg-white p-5 shadow-2xl dark:bg-[#111c33] border border-slate-200 dark:border-slate-800 animate-in slide-in-from-bottom-8 sm:zoom-in-95 duration-200 max-h-[85vh] flex flex-col">
            <h2 className="text-base font-bold text-slate-900 dark:text-white mb-3">
              Select your crop
            </h2>

            {/* Search Input */}
            <div className="relative flex items-center mb-4">
              <Search className="absolute left-3.5 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search"
                value={cropSearchQuery}
                onChange={(e) => setCropSearchQuery(e.target.value)}
                className="w-full rounded-full border border-slate-200 bg-white py-2 pl-9 pr-4 text-xs font-medium text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-white"
              />
            </div>

            {/* Grid of registered crops for this pesticide + other platform crops */}
            <div className="grid grid-cols-2 gap-3 overflow-y-auto py-2 flex-1">
              {activeFormulation.crops
                .filter((c) => c.cropName.toLowerCase().includes(cropSearchQuery.toLowerCase()))
                .map((c) => (
                  <button
                    key={c.cropName}
                    type="button"
                    onClick={() => {
                      setFormulationCrop(c);
                      setShowCropModal(false);
                      const matchGlobal = CROPS.find((cr) => cr.name.toLowerCase() === c.cropName.toLowerCase());
                      if (matchGlobal) setSelectedCrop(matchGlobal);

                      if (c.diseases.length > 1) {
                        setPendingSelectedDisease({ crop: c, disease: c.diseases[0] });
                        setShowDiseaseModal(true);
                      } else if (c.diseases.length === 1) {
                        setFormulationDisease(c.diseases[0]);
                        setProductDosage(c.diseases[0].dosage);
                        setDosageUnit(c.diseases[0].dosageUnit);
                        setWaterAmount(c.diseases[0].waterAmount);
                      }
                    }}
                    className="modal-crop-card flex flex-col items-center justify-center p-3 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-blue-500 hover:bg-blue-50/50 dark:hover:bg-slate-800/60 transition-all group"
                  >
                    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-3xl mb-2 group-hover:scale-105 transition-transform">
                      <span>{c.cropEmoji}</span>
                    </div>
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-100 text-center">
                      {c.cropName}
                    </span>
                    <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold">
                      {c.diseases.length} target{c.diseases.length > 1 ? "s" : ""}
                    </span>
                  </button>
                ))}

              {/* Other crops from full platform list */}
              {CROPS.filter(
                (cr) =>
                  !activeFormulation.crops.some(
                    (c) => c.cropName.toLowerCase() === cr.name.toLowerCase()
                  ) && cr.name.toLowerCase().includes(cropSearchQuery.toLowerCase())
              ).map((cr) => (
                <button
                  key={cr.name}
                  type="button"
                  onClick={() => {
                    const fallbackCrop: FormulationCropUse = {
                      cropName: cr.name,
                      cropEmoji: cr.emoji,
                      diseases: [
                        {
                          name: "General Pest / Disease Protection",
                          dosage: activeFormulation.crops[0]?.diseases[0]?.dosage || 250,
                          dosageUnit: activeFormulation.crops[0]?.diseases[0]?.dosageUnit || "ml/ac",
                          waterAmount: activeFormulation.crops[0]?.diseases[0]?.waterAmount || 200,
                          waterUnit: "l/ac",
                        },
                      ],
                    };
                    setFormulationCrop(fallbackCrop);
                    setFormulationDisease(fallbackCrop.diseases[0]);
                    setProductDosage(fallbackCrop.diseases[0].dosage);
                    setDosageUnit(fallbackCrop.diseases[0].dosageUnit);
                    setWaterAmount(fallbackCrop.diseases[0].waterAmount);
                    setSelectedCrop(cr);
                    setShowCropModal(false);
                  }}
                  className="modal-crop-card flex flex-col items-center justify-center p-3 rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-slate-50/40 dark:bg-slate-900/40 hover:border-blue-500 hover:bg-blue-50/40 dark:hover:bg-slate-800/60 transition-all group cursor-pointer"
                >
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-3xl mb-2 group-hover:scale-105 transition-transform">
                    <span>{cr.emoji}</span>
                  </div>
                  <span className="text-xs font-bold text-slate-800 dark:text-slate-100 text-center truncate w-full">
                    {cr.name}
                  </span>
                  <span className="text-[10px] text-slate-400 font-medium">
                    Other Crop
                  </span>
                </button>
              ))}
            </div>

            <div className="pt-3 mt-2 border-t border-slate-100 dark:border-slate-800 flex justify-end">
              <button
                type="button"
                onClick={() => setShowCropModal(false)}
                className="btn-21st btn-21st-secondary btn-21st-pill btn-21st-xs"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ─── MODAL: Select a disease (Screenshot 3) ─── */}
      {showDiseaseModal && activeFormulation && formulationCrop && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/70 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="modal-dialog-box relative w-full max-w-sm rounded-t-3xl sm:rounded-3xl bg-white p-5 shadow-2xl dark:bg-[#111c33] border border-slate-200 dark:border-slate-800 animate-in slide-in-from-bottom-8 sm:zoom-in-95 duration-200 max-h-[85vh] flex flex-col">
            <h2 className="text-base font-bold text-slate-900 dark:text-white mb-3">
              Select a disease
            </h2>

            <div className="overflow-y-auto py-1 flex-1 space-y-2.5">
              {/* Primary diseases for the chosen crop */}
              <div className="space-y-2">
                {formulationCrop.diseases.map((d) => {
                  const isSelected =
                    pendingSelectedDisease?.crop.cropName === formulationCrop.cropName &&
                    pendingSelectedDisease?.disease.name === d.name;
                  return (
                    <div
                      key={d.name}
                      onClick={() => setPendingSelectedDisease({ crop: formulationCrop, disease: d })}
                      className={`modal-disease-item flex items-center justify-between p-3.5 rounded-2xl border cursor-pointer transition-all ${
                        isSelected
                          ? "is-selected border-blue-600 bg-blue-50/70 dark:bg-blue-950/60 dark:border-blue-400 shadow-2xs"
                          : "border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                      }`}
                    >
                      <span className="text-xs font-bold text-slate-900 dark:text-white">
                        {d.name}
                      </span>
                      <div
                        className={`h-5 w-5 rounded-full border-2 flex items-center justify-center transition-colors ${
                          isSelected
                            ? "border-blue-600 bg-blue-600 dark:border-blue-400 dark:bg-blue-500"
                            : "border-slate-300 dark:border-slate-500"
                        }`}
                      >
                        {isSelected && <div className="h-2 w-2 rounded-full bg-white" />}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Additional diseases treatable with this product across other crops */}
              {activeFormulation.crops.some((c) => c.cropName !== formulationCrop.cropName) && (
                <div className="pt-3">
                  <h3 className="text-xs font-bold text-slate-900 dark:text-white mb-2">
                    Additional diseases treatable with this product
                  </h3>
                  <div className="rounded-xl bg-blue-50 dark:bg-blue-950/40 p-3 mb-2.5 flex items-start gap-2 text-[11px] text-blue-700 dark:text-blue-300">
                    <Info className="h-3.5 w-3.5 shrink-0 mt-0.5 text-blue-600 dark:text-blue-400" />
                    <span>Select another crop to see treatments for these diseases</span>
                  </div>

                  <div className="space-y-2">
                    {activeFormulation.crops
                      .filter((c) => c.cropName !== formulationCrop.cropName)
                      .flatMap((c) => c.diseases.map((d) => ({ crop: c, disease: d })))
                      .map(({ crop, disease }) => {
                        const isSelected =
                          pendingSelectedDisease?.crop.cropName === crop.cropName &&
                          pendingSelectedDisease?.disease.name === disease.name;
                        return (
                          <div
                            key={`${crop.cropName}-${disease.name}`}
                            onClick={() => setPendingSelectedDisease({ crop, disease })}
                            className={`modal-disease-item flex items-center justify-between p-3.5 rounded-2xl border cursor-pointer transition-all ${
                              isSelected
                                ? "is-selected border-blue-600 bg-blue-50/70 dark:bg-blue-950/60 dark:border-blue-400 shadow-2xs"
                                : "border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                            }`}
                          >
                            <div>
                              <span className="text-xs font-bold text-slate-900 dark:text-white block">
                                {disease.name}
                              </span>
                              <span className="text-[10px] text-slate-500 dark:text-slate-300">
                                in {crop.cropEmoji} {crop.cropName}
                              </span>
                            </div>
                            <div
                              className={`h-5 w-5 rounded-full border-2 flex items-center justify-center transition-colors ${
                                isSelected
                                  ? "border-blue-600 bg-blue-600 dark:border-blue-400 dark:bg-blue-500"
                                  : "border-slate-300 dark:border-slate-500"
                              }`}
                            >
                              {isSelected && <div className="h-2 w-2 rounded-full bg-white" />}
                            </div>
                          </div>
                        );
                      })}
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Actions: Cancel and OK */}
            <div className="pt-3 mt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <button
                type="button"
                onClick={() => setShowDiseaseModal(false)}
                className="btn-21st btn-21st-secondary btn-21st-pill btn-21st-xs"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={!pendingSelectedDisease}
                onClick={() => {
                  if (pendingSelectedDisease) {
                    setFormulationCrop(pendingSelectedDisease.crop);
                    setFormulationDisease(pendingSelectedDisease.disease);
                    setProductDosage(pendingSelectedDisease.disease.dosage);
                    setDosageUnit(pendingSelectedDisease.disease.dosageUnit);
                    setWaterAmount(pendingSelectedDisease.disease.waterAmount);
                    setShowDiseaseModal(false);

                    const matchGlobal = CROPS.find((cr) => cr.name.toLowerCase() === pendingSelectedDisease.crop.cropName.toLowerCase());
                    if (matchGlobal) setSelectedCrop(matchGlobal);
                  }
                }}
                className="btn-21st btn-21st-primary btn-21st-pill btn-21st-xs"
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Calculation Details (strictly matching reference photo) */}
      {showDetailsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="modal-dialog-box relative w-full max-w-sm rounded-3xl bg-white p-5 sm:p-6 shadow-2xl dark:bg-[#111c33] border border-slate-200 dark:border-slate-800 animate-in zoom-in-95 duration-200 max-h-[88vh] flex flex-col">
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              Calculation details
            </h2>

            <hr className="border-slate-200 dark:border-slate-800 my-3" />

            <div className="overflow-y-auto flex-1 pr-1 space-y-4 text-left">
              {(() => {
                const snap = lastCalculationSnapshot || (productDosage > 0 ? {
                  area,
                  areaUnit,
                  productDosage,
                  dosageUnit,
                  waterAmount,
                  pumpSize: effectivePumpSize,
                  totalProduct,
                  dosePerRefill,
                  pumpRefills,
                  baseProductUnit,
                } : null);

                if (!snap) {
                  return (
                    <div className="py-12 text-center text-xs text-slate-500 dark:text-slate-400">
                      <Calculator className="h-10 w-10 mx-auto mb-2 text-slate-300 dark:text-slate-600 stroke-[1.5]" />
                      <p className="font-bold text-sm text-slate-800 dark:text-slate-200">No calculation yet</p>
                      <p className="mt-1 text-slate-500 dark:text-slate-400">
                        Please enter product dosage or choose a formulation to see formula breakdown.
                      </p>
                    </div>
                  );
                }

                return (
                  <>
                    {/* Summary paragraph */}
                    <div className="text-xs leading-relaxed text-slate-700 dark:text-slate-300 space-y-1">
                      <p>
                        For {snap.area} {snap.areaUnit.toLowerCase()} use a total of {snap.totalProduct} {snap.baseProductUnit} of product.
                      </p>
                      <p>
                        For your {snap.pumpSize} l pump use {snap.dosePerRefill} {snap.baseProductUnit} per refill.
                      </p>
                      <p>
                        Refill your pump {snap.pumpRefills} times to treat the full area.
                      </p>
                    </div>

                    {/* Step 1: Total product */}
                    <div className="space-y-1">
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                        Total product
                      </h3>
                      <div>
                        <span className="block text-[11px] font-semibold text-slate-400">Formula</span>
                        <span className="text-xs text-slate-800 dark:text-slate-200 font-medium">
                          Area to treat × Product dosage
                        </span>
                      </div>
                      <div>
                        <span className="block text-[11px] font-semibold text-slate-400">Calculation</span>
                        <span className="text-xs text-slate-800 dark:text-slate-200 font-medium">
                          {snap.area} {snap.areaUnit.toLowerCase()} × {snap.productDosage} {snap.dosageUnit}
                        </span>
                      </div>
                      <div>
                        <span className="block text-[11px] font-semibold text-slate-400">Result</span>
                        <span className="text-sm font-extrabold text-slate-900 dark:text-white">
                          {snap.totalProduct} {snap.baseProductUnit}
                        </span>
                      </div>
                    </div>

                    {/* Step 2: Pump refills */}
                    <div className="space-y-1">
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                        Pump refills
                      </h3>
                      <div>
                        <span className="block text-[11px] font-semibold text-slate-400">Formula</span>
                        <span className="text-xs text-slate-800 dark:text-slate-200 font-medium">
                          (Water amount ÷ Pump size) × Area to treat
                        </span>
                      </div>
                      <div>
                        <span className="block text-[11px] font-semibold text-slate-400">Calculation</span>
                        <span className="text-xs text-slate-800 dark:text-slate-200 font-medium">
                          ({snap.waterAmount} l ÷ {snap.pumpSize} l) × {snap.area} {snap.areaUnit.toLowerCase()}
                        </span>
                      </div>
                      <div>
                        <span className="block text-[11px] font-semibold text-slate-400">Result</span>
                        <span className="text-sm font-extrabold text-slate-900 dark:text-white">
                          {snap.pumpRefills} times
                        </span>
                      </div>
                    </div>

                    {/* Step 3: Dose per refill */}
                    <div className="space-y-1">
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                        Dose per refill
                      </h3>
                      <div>
                        <span className="block text-[11px] font-semibold text-slate-400">Formula</span>
                        <span className="text-xs text-slate-800 dark:text-slate-200 font-medium">
                          Total product ÷ Pump refills
                        </span>
                      </div>
                      <div>
                        <span className="block text-[11px] font-semibold text-slate-400">Calculation</span>
                        <span className="text-xs text-slate-800 dark:text-slate-200 font-medium">
                          {snap.totalProduct} {snap.baseProductUnit} ÷ {snap.pumpRefills} times
                        </span>
                      </div>
                      <div>
                        <span className="block text-[11px] font-semibold text-slate-400">Result</span>
                        <span className="text-sm font-extrabold text-slate-900 dark:text-white">
                          {snap.dosePerRefill} {snap.baseProductUnit} per refill
                        </span>
                      </div>
                    </div>
                  </>
                );
              })()}
            </div>

            <hr className="border-slate-200 dark:border-slate-800 my-3" />

            {/* Bottom Close Button */}
            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => setShowDetailsModal(false)}
                className="btn-21st btn-21st-secondary btn-21st-pill btn-21st-sm px-6 font-bold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Measurement & Units Converter Helper */}
      {showMeasureModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="modal-dialog-box relative w-full max-w-sm rounded-3xl bg-white p-6 shadow-2xl dark:bg-[#111c33] border border-slate-200 dark:border-slate-800">
            <h2 className="text-base font-bold text-slate-900 dark:text-white mb-3">
              Indian Land Area Units
            </h2>
            <div className="space-y-2 text-xs text-slate-600 dark:text-slate-200 mb-6">
              <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                <span className="font-semibold text-slate-900 dark:text-white">1 Acre</span>
                <span>40 Gunta (43,560 sq ft)</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                <span className="font-semibold text-slate-900 dark:text-white">1 Hectare</span>
                <span>2.471 Acres (98.84 Gunta)</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                <span className="font-semibold text-slate-900 dark:text-white">1 Gunta</span>
                <span>1,089 sq ft (0.025 Acre)</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-100 dark:border-slate-800">
                <span className="font-semibold text-slate-900 dark:text-white">1 Bigha (Central)</span>
                <span>~0.625 Acre (varies by state)</span>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setShowMeasureModal(false)}
              className="btn-21st btn-21st-primary btn-21st-pill w-full py-2.5 text-xs font-bold"
            >
              Got it
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
