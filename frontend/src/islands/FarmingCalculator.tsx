import * as React from "react";
import {
  ArrowLeft,
  Volume2,
  VolumeX,
  Plus,
  Minus,
  Search,
  Sparkles,
  Droplets,
  Sun,
  CloudRain,
  Snowflake,
  ShieldAlert,
  Layers,
  ThermometerSun,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  TrendingUp,
  Coins,
  Scale,
  Settings2,
} from "lucide-react";

/**
 * Exact Seed Requirement Calculation Function requested for Farming Calculator.
 * Calculates target plant count, seeds needed (adjusted for germination & purity),
 * and total seed weight in kilograms.
 */
export function calculateSeedRequirement({
  areaAcres,
  rowSpacingInches,
  plantSpacingInches,
  germinationRate = 0.9,
  purityRate = 0.98,
  seedWeightGramsPerThousand = 40,
}: {
  areaAcres: number;
  rowSpacingInches: number;
  plantSpacingInches: number;
  germinationRate?: number;
  purityRate?: number;
  seedWeightGramsPerThousand?: number;
}) {
  const areaSquareInches = areaAcres * 43560 * 144;
  const spacePerPlantSquareInches = rowSpacingInches * plantSpacingInches;
  const targetPlantCount = areaSquareInches / (spacePerPlantSquareInches > 0 ? spacePerPlantSquareInches : 1);

  const germ = Math.max(0.01, Math.min(1.0, germinationRate));
  const purity = Math.max(0.01, Math.min(1.0, purityRate));
  const seedsNeeded = targetPlantCount / (germ * purity);
  const totalWeightKg = (seedsNeeded * seedWeightGramsPerThousand) / 1000 / 1000;

  return {
    totalPlants: Math.round(targetPlantCount),
    totalSeeds: Math.round(seedsNeeded),
    totalWeightKg: Number(totalWeightKg.toFixed(2)),
  };
}

/**
 * Crop Yield & Net Margin Calculation Function.
 * Estimates harvest production, gross revenues, cultivation expenditures,
 * net profits, and Return on Investment (ROI %).
 */
export function calculateCropYieldAndNetMargin({
  areaAcres,
  expectedYieldPerAcreQtl,
  sellingPricePerQtl,
  costOfCultivationPerAcre,
}: {
  areaAcres: number;
  expectedYieldPerAcreQtl: number;
  sellingPricePerQtl: number;
  costOfCultivationPerAcre: number;
}) {
  const area = Math.max(0.01, areaAcres);
  const totalProductionQtl = expectedYieldPerAcreQtl * area;
  const totalProductionTonnes = totalProductionQtl / 10;
  const grossRevenue = totalProductionQtl * sellingPricePerQtl;
  const totalCost = costOfCultivationPerAcre * area;
  const netMargin = grossRevenue - totalCost;
  const netMarginPerAcre = area > 0 ? netMargin / area : 0;
  const roiPercent = totalCost > 0 ? (netMargin / totalCost) * 100 : 0;
  const benefitCostRatio = totalCost > 0 ? grossRevenue / totalCost : 0;

  return {
    totalProductionQtl: Number(totalProductionQtl.toFixed(1)),
    totalProductionTonnes: Number(totalProductionTonnes.toFixed(2)),
    grossRevenue: Math.round(grossRevenue),
    totalCost: Math.round(totalCost),
    netMargin: Math.round(netMargin),
    netMarginPerAcre: Math.round(netMarginPerAcre),
    roiPercent: Number(roiPercent.toFixed(1)),
    benefitCostRatio: Number(benefitCostRatio.toFixed(2)),
  };
}

interface CropInfo {
  name: string;
  emoji: string;
  n: number; // kg/ha
  p: number; // kg/ha
  k: number; // kg/ha
  category: string;
  defaultRowSpacing: number; // inches
  defaultPlantSpacing: number; // inches
  defaultSeedWeightThousand: number; // grams / 1000 seeds
  defaultYieldPerAcreQtl: number; // Quintals per acre
  defaultPricePerQtl: number; // ₹ per Quintal (MSP or market average)
  defaultCostPerAcre: number; // ₹ per acre estimated cultivation cost
}

const COMMON_CROPS: CropInfo[] = [
  // ─── Cereals & Millets ───
  {
    name: "Maize",
    emoji: "🌽",
    n: 120,
    p: 60,
    k: 40,
    category: "Cereal / Grain",
    defaultRowSpacing: 24,
    defaultPlantSpacing: 8,
    defaultSeedWeightThousand: 280,
    defaultYieldPerAcreQtl: 28,
    defaultPricePerQtl: 2225,
    defaultCostPerAcre: 18000,
  },
  {
    name: "Rice",
    emoji: "🌾",
    n: 120,
    p: 50,
    k: 50,
    category: "Cereal / Grain",
    defaultRowSpacing: 8,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 25,
    defaultYieldPerAcreQtl: 22,
    defaultPricePerQtl: 2300,
    defaultCostPerAcre: 22000,
  },
  {
    name: "Wheat",
    emoji: "🌾",
    n: 120,
    p: 60,
    k: 40,
    category: "Cereal / Grain",
    defaultRowSpacing: 8,
    defaultPlantSpacing: 2,
    defaultSeedWeightThousand: 40,
    defaultYieldPerAcreQtl: 20,
    defaultPricePerQtl: 2275,
    defaultCostPerAcre: 16000,
  },
  {
    name: "Bajra",
    emoji: "🌾",
    n: 80,
    p: 40,
    k: 20,
    category: "Millet / Cereal",
    defaultRowSpacing: 18,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 8,
    defaultYieldPerAcreQtl: 14,
    defaultPricePerQtl: 2625,
    defaultCostPerAcre: 12000,
  },
  {
    name: "Jowar",
    emoji: "🌾",
    n: 80,
    p: 40,
    k: 40,
    category: "Millet / Cereal",
    defaultRowSpacing: 18,
    defaultPlantSpacing: 6,
    defaultSeedWeightThousand: 30,
    defaultYieldPerAcreQtl: 15,
    defaultPricePerQtl: 3371,
    defaultCostPerAcre: 13000,
  },
  {
    name: "Ragi",
    emoji: "🌾",
    n: 60,
    p: 30,
    k: 30,
    category: "Millet / Cereal",
    defaultRowSpacing: 10,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 3.5,
    defaultYieldPerAcreQtl: 12,
    defaultPricePerQtl: 4290,
    defaultCostPerAcre: 12000,
  },
  {
    name: "Barley",
    emoji: "🌾",
    n: 60,
    p: 30,
    k: 20,
    category: "Cereal / Grain",
    defaultRowSpacing: 9,
    defaultPlantSpacing: 2,
    defaultSeedWeightThousand: 42,
    defaultYieldPerAcreQtl: 16,
    defaultPricePerQtl: 1850,
    defaultCostPerAcre: 13000,
  },

  // ─── Pulses & Legumes ───
  {
    name: "Pigeonpea",
    emoji: "🫘",
    n: 25,
    p: 50,
    k: 20,
    category: "Pulse / Legume",
    defaultRowSpacing: 36,
    defaultPlantSpacing: 12,
    defaultSeedWeightThousand: 110,
    defaultYieldPerAcreQtl: 8,
    defaultPricePerQtl: 7550,
    defaultCostPerAcre: 16000,
  },
  {
    name: "Chickpea",
    emoji: "🫘",
    n: 20,
    p: 40,
    k: 20,
    category: "Pulse / Legume",
    defaultRowSpacing: 12,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 220,
    defaultYieldPerAcreQtl: 8,
    defaultPricePerQtl: 5440,
    defaultCostPerAcre: 14000,
  },
  {
    name: "Green Gram",
    emoji: "🫘",
    n: 20,
    p: 40,
    k: 20,
    category: "Pulse / Legume",
    defaultRowSpacing: 12,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 45,
    defaultYieldPerAcreQtl: 5,
    defaultPricePerQtl: 8682,
    defaultCostPerAcre: 11000,
  },
  {
    name: "Black Gram",
    emoji: "🫘",
    n: 20,
    p: 40,
    k: 20,
    category: "Pulse / Legume",
    defaultRowSpacing: 12,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 42,
    defaultYieldPerAcreQtl: 5,
    defaultPricePerQtl: 7400,
    defaultCostPerAcre: 11000,
  },
  {
    name: "Lentil",
    emoji: "🫘",
    n: 20,
    p: 40,
    k: 20,
    category: "Pulse / Legume",
    defaultRowSpacing: 9,
    defaultPlantSpacing: 2.5,
    defaultSeedWeightThousand: 28,
    defaultYieldPerAcreQtl: 6,
    defaultPricePerQtl: 6425,
    defaultCostPerAcre: 12000,
  },
  {
    name: "Field Pea",
    emoji: "🫛",
    n: 25,
    p: 50,
    k: 25,
    category: "Pulse / Legume",
    defaultRowSpacing: 12,
    defaultPlantSpacing: 3,
    defaultSeedWeightThousand: 200,
    defaultYieldPerAcreQtl: 10,
    defaultPricePerQtl: 4500,
    defaultCostPerAcre: 15000,
  },
  {
    name: "Cowpea",
    emoji: "🫘",
    n: 25,
    p: 50,
    k: 25,
    category: "Pulse / Legume",
    defaultRowSpacing: 18,
    defaultPlantSpacing: 6,
    defaultSeedWeightThousand: 140,
    defaultYieldPerAcreQtl: 7,
    defaultPricePerQtl: 5200,
    defaultCostPerAcre: 13000,
  },

  // ─── Oilseeds ───
  {
    name: "Groundnut",
    emoji: "🥜",
    n: 25,
    p: 50,
    k: 75,
    category: "Oilseed / Legume",
    defaultRowSpacing: 12,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 450,
    defaultYieldPerAcreQtl: 12,
    defaultPricePerQtl: 6377,
    defaultCostPerAcre: 22000,
  },
  {
    name: "Soybean",
    emoji: "🫘",
    n: 30,
    p: 60,
    k: 40,
    category: "Oilseed / Legume",
    defaultRowSpacing: 18,
    defaultPlantSpacing: 3,
    defaultSeedWeightThousand: 120,
    defaultYieldPerAcreQtl: 10,
    defaultPricePerQtl: 4892,
    defaultCostPerAcre: 15000,
  },
  {
    name: "Mustard",
    emoji: "🌼",
    n: 80,
    p: 40,
    k: 40,
    category: "Oilseed",
    defaultRowSpacing: 18,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 5,
    defaultYieldPerAcreQtl: 7,
    defaultPricePerQtl: 5650,
    defaultCostPerAcre: 12000,
  },
  {
    name: "Sunflower",
    emoji: "🌻",
    n: 60,
    p: 60,
    k: 30,
    category: "Oilseed",
    defaultRowSpacing: 24,
    defaultPlantSpacing: 12,
    defaultSeedWeightThousand: 55,
    defaultYieldPerAcreQtl: 8,
    defaultPricePerQtl: 7280,
    defaultCostPerAcre: 14000,
  },
  {
    name: "Sesame",
    emoji: "🌱",
    n: 40,
    p: 25,
    k: 25,
    category: "Oilseed",
    defaultRowSpacing: 12,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 3,
    defaultYieldPerAcreQtl: 3,
    defaultPricePerQtl: 9267,
    defaultCostPerAcre: 10000,
  },
  {
    name: "Castor",
    emoji: "🌱",
    n: 80,
    p: 40,
    k: 20,
    category: "Commercial / Oilseed",
    defaultRowSpacing: 36,
    defaultPlantSpacing: 24,
    defaultSeedWeightThousand: 300,
    defaultYieldPerAcreQtl: 10,
    defaultPricePerQtl: 6000,
    defaultCostPerAcre: 16000,
  },
  {
    name: "Safflower",
    emoji: "🌼",
    n: 50,
    p: 40,
    k: 20,
    category: "Oilseed",
    defaultRowSpacing: 18,
    defaultPlantSpacing: 8,
    defaultSeedWeightThousand: 45,
    defaultYieldPerAcreQtl: 6,
    defaultPricePerQtl: 5800,
    defaultCostPerAcre: 11000,
  },

  // ─── Commercial & Fibre ───
  {
    name: "Cotton",
    emoji: "☁️",
    n: 120,
    p: 60,
    k: 60,
    category: "Commercial / Fibre",
    defaultRowSpacing: 36,
    defaultPlantSpacing: 18,
    defaultSeedWeightThousand: 100,
    defaultYieldPerAcreQtl: 10,
    defaultPricePerQtl: 7121,
    defaultCostPerAcre: 28000,
  },
  {
    name: "Sugarcane",
    emoji: "🎋",
    n: 250,
    p: 100,
    k: 120,
    category: "Cash / Commercial",
    defaultRowSpacing: 48,
    defaultPlantSpacing: 12,
    defaultSeedWeightThousand: 50000,
    defaultYieldPerAcreQtl: 350,
    defaultPricePerQtl: 315,
    defaultCostPerAcre: 40000,
  },
  {
    name: "Jute",
    emoji: "🎋",
    n: 60,
    p: 30,
    k: 30,
    category: "Commercial / Fibre",
    defaultRowSpacing: 12,
    defaultPlantSpacing: 3,
    defaultSeedWeightThousand: 2.5,
    defaultYieldPerAcreQtl: 14,
    defaultPricePerQtl: 5335,
    defaultCostPerAcre: 18000,
  },
  {
    name: "Tobacco",
    emoji: "🍃",
    n: 100,
    p: 50,
    k: 100,
    category: "Cash Crop",
    defaultRowSpacing: 36,
    defaultPlantSpacing: 24,
    defaultSeedWeightThousand: 0.1,
    defaultYieldPerAcreQtl: 10,
    defaultPricePerQtl: 12000,
    defaultCostPerAcre: 35000,
  },

  // ─── Vegetables ───
  {
    name: "Tomato",
    emoji: "🍅",
    n: 150,
    p: 100,
    k: 120,
    category: "Vegetable",
    defaultRowSpacing: 30,
    defaultPlantSpacing: 18,
    defaultSeedWeightThousand: 3.2,
    defaultYieldPerAcreQtl: 150,
    defaultPricePerQtl: 1800,
    defaultCostPerAcre: 55000,
  },
  {
    name: "Potato",
    emoji: "🥔",
    n: 180,
    p: 100,
    k: 150,
    category: "Tuber / Vegetable",
    defaultRowSpacing: 24,
    defaultPlantSpacing: 8,
    defaultSeedWeightThousand: 40000,
    defaultYieldPerAcreQtl: 100,
    defaultPricePerQtl: 1200,
    defaultCostPerAcre: 45000,
  },
  {
    name: "Onion",
    emoji: "🧅",
    n: 100,
    p: 50,
    k: 80,
    category: "Vegetable",
    defaultRowSpacing: 6,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 3.8,
    defaultYieldPerAcreQtl: 90,
    defaultPricePerQtl: 2000,
    defaultCostPerAcre: 45000,
  },
  {
    name: "Chilli",
    emoji: "🌶️",
    n: 120,
    p: 60,
    k: 60,
    category: "Spice / Vegetable",
    defaultRowSpacing: 24,
    defaultPlantSpacing: 18,
    defaultSeedWeightThousand: 4.5,
    defaultYieldPerAcreQtl: 15,
    defaultPricePerQtl: 14000,
    defaultCostPerAcre: 60000,
  },
  {
    name: "Brinjal",
    emoji: "🍆",
    n: 120,
    p: 80,
    k: 60,
    category: "Vegetable",
    defaultRowSpacing: 30,
    defaultPlantSpacing: 24,
    defaultSeedWeightThousand: 4,
    defaultYieldPerAcreQtl: 140,
    defaultPricePerQtl: 1500,
    defaultCostPerAcre: 40000,
  },
  {
    name: "Cabbage",
    emoji: "🥬",
    n: 150,
    p: 80,
    k: 90,
    category: "Vegetable",
    defaultRowSpacing: 24,
    defaultPlantSpacing: 18,
    defaultSeedWeightThousand: 3.5,
    defaultYieldPerAcreQtl: 120,
    defaultPricePerQtl: 1200,
    defaultCostPerAcre: 35000,
  },
  {
    name: "Cauliflower",
    emoji: "🥦",
    n: 150,
    p: 80,
    k: 90,
    category: "Vegetable",
    defaultRowSpacing: 24,
    defaultPlantSpacing: 18,
    defaultSeedWeightThousand: 3.5,
    defaultYieldPerAcreQtl: 100,
    defaultPricePerQtl: 1500,
    defaultCostPerAcre: 35000,
  },
  {
    name: "Okra",
    emoji: "🌱",
    n: 80,
    p: 50,
    k: 50,
    category: "Vegetable",
    defaultRowSpacing: 18,
    defaultPlantSpacing: 12,
    defaultSeedWeightThousand: 60,
    defaultYieldPerAcreQtl: 45,
    defaultPricePerQtl: 2500,
    defaultCostPerAcre: 30000,
  },
  {
    name: "Capsicum",
    emoji: "🫑",
    n: 150,
    p: 100,
    k: 120,
    category: "Vegetable",
    defaultRowSpacing: 24,
    defaultPlantSpacing: 18,
    defaultSeedWeightThousand: 6,
    defaultYieldPerAcreQtl: 80,
    defaultPricePerQtl: 3500,
    defaultCostPerAcre: 65000,
  },
  {
    name: "Cucumber",
    emoji: "🥒",
    n: 120,
    p: 60,
    k: 60,
    category: "Cucurbit / Vegetable",
    defaultRowSpacing: 48,
    defaultPlantSpacing: 24,
    defaultSeedWeightThousand: 25,
    defaultYieldPerAcreQtl: 80,
    defaultPricePerQtl: 1400,
    defaultCostPerAcre: 32000,
  },
  {
    name: "Bitter Gourd",
    emoji: "🥒",
    n: 100,
    p: 60,
    k: 60,
    category: "Cucurbit / Vegetable",
    defaultRowSpacing: 60,
    defaultPlantSpacing: 24,
    defaultSeedWeightThousand: 160,
    defaultYieldPerAcreQtl: 50,
    defaultPricePerQtl: 2800,
    defaultCostPerAcre: 38000,
  },
  {
    name: "Bottle Gourd",
    emoji: "🥒",
    n: 80,
    p: 50,
    k: 50,
    category: "Cucurbit / Vegetable",
    defaultRowSpacing: 72,
    defaultPlantSpacing: 36,
    defaultSeedWeightThousand: 180,
    defaultYieldPerAcreQtl: 120,
    defaultPricePerQtl: 1200,
    defaultCostPerAcre: 32000,
  },
  {
    name: "Watermelon",
    emoji: "🍉",
    n: 100,
    p: 60,
    k: 60,
    category: "Fruit / Cucurbit",
    defaultRowSpacing: 72,
    defaultPlantSpacing: 36,
    defaultSeedWeightThousand: 50,
    defaultYieldPerAcreQtl: 150,
    defaultPricePerQtl: 1000,
    defaultCostPerAcre: 35000,
  },
  {
    name: "Muskmelon",
    emoji: "🍈",
    n: 100,
    p: 60,
    k: 60,
    category: "Fruit / Cucurbit",
    defaultRowSpacing: 60,
    defaultPlantSpacing: 24,
    defaultSeedWeightThousand: 35,
    defaultYieldPerAcreQtl: 80,
    defaultPricePerQtl: 1600,
    defaultCostPerAcre: 32000,
  },
  {
    name: "Carrot",
    emoji: "🥕",
    n: 80,
    p: 50,
    k: 80,
    category: "Root / Vegetable",
    defaultRowSpacing: 9,
    defaultPlantSpacing: 3,
    defaultSeedWeightThousand: 1.5,
    defaultYieldPerAcreQtl: 90,
    defaultPricePerQtl: 1800,
    defaultCostPerAcre: 30000,
  },
  {
    name: "Radish",
    emoji: "🥕",
    n: 60,
    p: 40,
    k: 50,
    category: "Root / Vegetable",
    defaultRowSpacing: 12,
    defaultPlantSpacing: 3,
    defaultSeedWeightThousand: 8,
    defaultYieldPerAcreQtl: 80,
    defaultPricePerQtl: 1200,
    defaultCostPerAcre: 20000,
  },
  {
    name: "Spinach",
    emoji: "🥬",
    n: 80,
    p: 40,
    k: 40,
    category: "Leafy Vegetable",
    defaultRowSpacing: 8,
    defaultPlantSpacing: 3,
    defaultSeedWeightThousand: 10,
    defaultYieldPerAcreQtl: 60,
    defaultPricePerQtl: 1500,
    defaultCostPerAcre: 22000,
  },

  // ─── Spices & Plantation ───
  {
    name: "Garlic",
    emoji: "🧄",
    n: 100,
    p: 50,
    k: 50,
    category: "Spice / Bulb",
    defaultRowSpacing: 6,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 1500,
    defaultYieldPerAcreQtl: 35,
    defaultPricePerQtl: 8000,
    defaultCostPerAcre: 45000,
  },
  {
    name: "Ginger",
    emoji: "🫚",
    n: 100,
    p: 50,
    k: 100,
    category: "Spice / Rhizome",
    defaultRowSpacing: 12,
    defaultPlantSpacing: 8,
    defaultSeedWeightThousand: 20000,
    defaultYieldPerAcreQtl: 60,
    defaultPricePerQtl: 6000,
    defaultCostPerAcre: 70000,
  },
  {
    name: "Turmeric",
    emoji: "🌿",
    n: 120,
    p: 60,
    k: 120,
    category: "Spice / Rhizome",
    defaultRowSpacing: 18,
    defaultPlantSpacing: 8,
    defaultSeedWeightThousand: 25000,
    defaultYieldPerAcreQtl: 80,
    defaultPricePerQtl: 7500,
    defaultCostPerAcre: 65000,
  },
  {
    name: "Coriander",
    emoji: "🌿",
    n: 50,
    p: 30,
    k: 20,
    category: "Spice / Herb",
    defaultRowSpacing: 10,
    defaultPlantSpacing: 4,
    defaultSeedWeightThousand: 12,
    defaultYieldPerAcreQtl: 6,
    defaultPricePerQtl: 7000,
    defaultCostPerAcre: 15000,
  },
  {
    name: "Cumin",
    emoji: "🌿",
    n: 30,
    p: 20,
    k: 10,
    category: "Spice",
    defaultRowSpacing: 9,
    defaultPlantSpacing: 3,
    defaultSeedWeightThousand: 4,
    defaultYieldPerAcreQtl: 3.5,
    defaultPricePerQtl: 22000,
    defaultCostPerAcre: 18000,
  },
  {
    name: "Cardamom",
    emoji: "🌿",
    n: 75,
    p: 75,
    k: 150,
    category: "Spice / Plantation",
    defaultRowSpacing: 72,
    defaultPlantSpacing: 72,
    defaultSeedWeightThousand: 20,
    defaultYieldPerAcreQtl: 2,
    defaultPricePerQtl: 150000,
    defaultCostPerAcre: 80000,
  },
  {
    name: "Tea",
    emoji: "🍵",
    n: 150,
    p: 40,
    k: 100,
    category: "Plantation",
    defaultRowSpacing: 42,
    defaultPlantSpacing: 30,
    defaultSeedWeightThousand: 1000,
    defaultYieldPerAcreQtl: 25,
    defaultPricePerQtl: 18000,
    defaultCostPerAcre: 75000,
  },
  {
    name: "Coffee",
    emoji: "☕",
    n: 140,
    p: 90,
    k: 140,
    category: "Plantation",
    defaultRowSpacing: 84,
    defaultPlantSpacing: 84,
    defaultSeedWeightThousand: 400,
    defaultYieldPerAcreQtl: 10,
    defaultPricePerQtl: 30000,
    defaultCostPerAcre: 60000,
  },

  // ─── Fruits ───
  {
    name: "Banana",
    emoji: "🍌",
    n: 200,
    p: 60,
    k: 300,
    category: "Fruit / Cash",
    defaultRowSpacing: 72,
    defaultPlantSpacing: 72,
    defaultSeedWeightThousand: 100000,
    defaultYieldPerAcreQtl: 300,
    defaultPricePerQtl: 1500,
    defaultCostPerAcre: 70000,
  },
  {
    name: "Papaya",
    emoji: "🍈",
    n: 150,
    p: 150,
    k: 200,
    category: "Fruit / Cash",
    defaultRowSpacing: 72,
    defaultPlantSpacing: 72,
    defaultSeedWeightThousand: 15,
    defaultYieldPerAcreQtl: 250,
    defaultPricePerQtl: 1200,
    defaultCostPerAcre: 50000,
  },
  {
    name: "Mango",
    emoji: "🥭",
    n: 100,
    p: 50,
    k: 100,
    category: "Fruit / Orchard",
    defaultRowSpacing: 300,
    defaultPlantSpacing: 300,
    defaultSeedWeightThousand: 500000,
    defaultYieldPerAcreQtl: 60,
    defaultPricePerQtl: 3500,
    defaultCostPerAcre: 35000,
  },
  {
    name: "Pomegranate",
    emoji: "🍎",
    n: 125,
    p: 60,
    k: 125,
    category: "Fruit / Orchard",
    defaultRowSpacing: 144,
    defaultPlantSpacing: 120,
    defaultSeedWeightThousand: 35,
    defaultYieldPerAcreQtl: 50,
    defaultPricePerQtl: 7000,
    defaultCostPerAcre: 65000,
  },
];

// High-frequency popular targeted crops for quick 1-tap pills
const QUICK_TARGET_CROPS = [
  "Maize",
  "Rice",
  "Wheat",
  "Pigeonpea",
  "Groundnut",
  "Cotton",
  "Soybean",
  "Tomato",
  "Chilli",
  "Onion",
  "Mustard",
  "Potato",
];

const SEASONS = [
  { id: "Summer", label: "Summer / Zaid", icon: Sun, desc: "High heat >35°C, high VPD" },
  { id: "Kharif", label: "Kharif / Monsoon", icon: CloudRain, desc: "Monsoon rains & fast weed flush" },
  { id: "Rabi", label: "Rabi / Winter", icon: Snowflake, desc: "Cool weather & residual moisture" },
];

const SOIL_TYPES = [
  "Loamy",
  "Sandy",
  "Clay",
  "Black Cotton",
  "Red / Laterite",
  "Alluvial",
];

const IRRIGATION_STATUSES = [
  "Drip",
  "Sprinkler",
  "Flood irrigated",
  "Rainfed",
];

const WEED_PRESSURES = [
  { id: "none", label: "None (0%)", badge: "0% Cover", buffer: 0, penalty: 0 },
  { id: "low", label: "Low (<15%)", badge: "<15% Cover", buffer: 8, penalty: 10 },
  { id: "moderate", label: "Moderate (15–35%)", badge: "15–35% Cover", buffer: 20, penalty: 25 },
  { id: "severe", label: "Severe (>35%)", badge: ">35% Cover", buffer: 25, penalty: 40 },
];

const AVAILABLE_WEED_TYPES = [
  { id: "broadleaf", label: "Broadleaf Weeds (Bathua, Chaulai, etc.)", isInvasive: false },
  { id: "grasses", label: "Annual Grasses (Sawank, Doob grass)", isInvasive: false },
  { id: "sedges", label: "Sedges / Cyperus spp.", isInvasive: true },
  { id: "parthenium", label: "Parthenium hysterophorus (Congress grass)", isInvasive: true },
  { id: "cyperus_rotundus", label: "Cyperus rotundus (Purple nutsedge / Motha)", isInvasive: true },
  { id: "striga", label: "Striga (Witchweed)", isInvasive: true },
];

export default function FarmingCalculator() {
  // Input parameters
  const [selectedCrop, setSelectedCrop] = React.useState<string>("Maize");
  const [cropSearch, setCropSearch] = React.useState<string>("");
  const [isCropDropdownOpen, setIsCropDropdownOpen] = React.useState<boolean>(false);
  const dropdownRef = React.useRef<HTMLDivElement>(null);

  const [fieldSize, setFieldSize] = React.useState<number>(1.0);
  const [fieldUnit, setFieldUnit] = React.useState<"Acre" | "Hectare" | "Gunta">("Acre");

  const [season, setSeason] = React.useState<string>("Summer");
  const [soilType, setSoilType] = React.useState<string>("Loamy");
  const [irrigationStatus, setIrrigationStatus] = React.useState<string>("Drip");
  const [weedPressure, setWeedPressure] = React.useState<string>("Moderate (15–35%)");
  const [selectedWeeds, setSelectedWeeds] = React.useState<string[]>([
    "Broadleaf Weeds (Bathua, Chaulai, etc.)",
    "Parthenium hysterophorus (Congress grass)",
  ]);

  // Seed & Spacing Customizable Inputs
  const [rowSpacingInches, setRowSpacingInches] = React.useState<number>(24);
  const [plantSpacingInches, setPlantSpacingInches] = React.useState<number>(8);
  const [germinationPercent, setGerminationPercent] = React.useState<number>(90);
  const [purityPercent, setPurityPercent] = React.useState<number>(98);
  const [seedWeightGramsThousand, setSeedWeightGramsThousand] = React.useState<number>(280);

  // Crop Yield & Net Margin Customizable Inputs
  const [expectedYieldQtlAc, setExpectedYieldQtlAc] = React.useState<number>(28);
  const [sellingPriceQtl, setSellingPriceQtl] = React.useState<number>(2225);
  const [costOfCultivationAc, setCostOfCultivationAc] = React.useState<number>(18000);
  const [showAdvancedSettings, setShowAdvancedSettings] = React.useState<boolean>(false);

  // Results View Active Tab: 'all' | 'nutrition' | 'seed' | 'economics'
  const [activeTab, setActiveTab] = React.useState<"all" | "nutrition" | "seed" | "economics">("all");

  // UI state
  const [hasCalculated, setHasCalculated] = React.useState<boolean>(false);
  const [isCalculating, setIsCalculating] = React.useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = React.useState<boolean>(false);
  const resultsRef = React.useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsCropDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const currentCropObj =
    COMMON_CROPS.find((c) => c.name.toLowerCase() === selectedCrop.toLowerCase()) || {
      name: selectedCrop,
      emoji: "🌱",
      n: 100,
      p: 50,
      k: 50,
      category: "Field Crop",
      defaultRowSpacing: 18,
      defaultPlantSpacing: 6,
      defaultSeedWeightThousand: 40,
      defaultYieldPerAcreQtl: 15,
      defaultPricePerQtl: 2500,
      defaultCostPerAcre: 20000,
    };

  // Synchronize defaults when crop changes
  const handleCropSelect = (cropName: string) => {
    setSelectedCrop(cropName);
    setIsCropDropdownOpen(false);
    const found = COMMON_CROPS.find((c) => c.name.toLowerCase() === cropName.toLowerCase());
    if (found) {
      setRowSpacingInches(found.defaultRowSpacing);
      setPlantSpacingInches(found.defaultPlantSpacing);
      setSeedWeightGramsThousand(found.defaultSeedWeightThousand);
      setExpectedYieldQtlAc(found.defaultYieldPerAcreQtl);
      setSellingPriceQtl(found.defaultPricePerQtl);
      setCostOfCultivationAc(found.defaultCostPerAcre);
    }
  };

  // Filter crops by name or category
  const filteredCrops = COMMON_CROPS.filter(
    (c) =>
      c.name.toLowerCase().includes(cropSearch.toLowerCase()) ||
      c.category.toLowerCase().includes(cropSearch.toLowerCase())
  );

  // Unit conversion
  const acres =
    fieldUnit === "Acre"
      ? fieldSize
      : fieldUnit === "Hectare"
      ? fieldSize * 2.47105
      : fieldSize / 40.0;
  const hectares = acres * 0.404686;
  const guntas = acres * 40.0;

  // Rule A & Agronomic Evaluation
  const wpLower = weedPressure.toLowerCase();
  const isSevereWeeds = wpLower.includes("severe") || wpLower.includes(">35");
  const isModerateWeeds =
    wpLower.includes("moderate") || wpLower.includes("15–35") || wpLower.includes("15-35");
  const isLowWeeds = wpLower.includes("low") || wpLower.includes("<15");

  let bufferPercent = 0;
  let weedLossPenaltyPct = 0;
  let applicationMethodTitle = "Standard Root-Zone Placement";
  let applicationMethodDetail =
    "Apply basal fertilizer directly along seed furrows, followed by scheduled split top-dressing.";
  let basalSplitPct = 50;
  let topdress1SplitPct = 50;
  let topdress2SplitPct = 0;

  if (isSevereWeeds) {
    bufferPercent = 25;
    weedLossPenaltyPct = 40;
    applicationMethodTitle = "Root-zone Deep Band Placement (7–10 cm depth) or Drip Fertigation";
    applicationMethodDetail =
      "CRITICAL: Nutrient efficiency drops by >40% under severe weed competition! NEVER broadcast fertilizer across open soil. Implement immediate mechanical intervention (inter-row power weeder, wheel hoe, or manual ring weeding) during the Critical Period of Weed Control (CPWC). Delay top-dress fertilizer until 24–48 hours AFTER weeds are cleared, then band nutrients directly into the crop root zone at 7–10 cm depth.";
    basalSplitPct = 30;
    topdress1SplitPct = 35;
    topdress2SplitPct = 35;
  } else if (isModerateWeeds) {
    bufferPercent = 20;
    weedLossPenaltyPct = 25;
    applicationMethodTitle = "Split-Dose Root-Zone Band Placement (5–10 cm depth) or Drip Fertigation";
    applicationMethodDetail =
      "Weeds intercept 20–30% of applied nitrogen and phosphorus. DO NOT dump all excess fertilizer at once—broadcasting open-surface fertilizer primarily feeds weed competition! Deliver nutrients via split-dose banding directly at the crop root zone (5–10 cm depth) or via drip fertigation across 3 balanced splits.";
    basalSplitPct = 30;
    topdress1SplitPct = 35;
    topdress2SplitPct = 35;
  } else if (isLowWeeds) {
    bufferPercent = 8;
    weedLossPenaltyPct = 8;
    applicationMethodTitle = "Root-zone Band Placement or Side Furrow Dressing";
    applicationMethodDetail =
      "A 5–10% compensatory nutrient buffer is added to safeguard crop vigor. Carry out early targeted spot weeding (ring weeding) around weed patches without altering overall basal dose timing. Band fertilizers 5 cm away from crop stems rather than wide broadcasting.";
    basalSplitPct = 40;
    topdress1SplitPct = 40;
    topdress2SplitPct = 20;
  }

  // Pure nutrient calculations (kg)
  const baselineN = currentCropObj.n * hectares;
  const baselineP = currentCropObj.p * hectares;
  const baselineK = currentCropObj.k * hectares;

  const multiplier = 1 + bufferPercent / 100;
  const adjustedN = baselineN * multiplier;
  const adjustedP = baselineP * multiplier;
  const adjustedK = baselineK * multiplier;

  // Commercial fertilizers (50kg bags)
  const dapKg = adjustedP / 0.46;
  const dapNSupplied = dapKg * 0.18;
  const remainingN = Math.max(0, adjustedN - dapNSupplied);
  const ureaKg = remainingN / 0.46;
  const mopKg = adjustedK / 0.60;

  const dapBags = (dapKg / 50).toFixed(1);
  const ureaBags = (ureaKg / 50).toFixed(1);
  const mopBags = (mopKg / 50).toFixed(1);

  // Rule B: Summer Season Weed Strategy
  const isSummerSeason = season.toLowerCase().includes("summer");

  // Analyze weed categories
  const invasiveWeeds = selectedWeeds.filter((w) => {
    const l = w.toLowerCase();
    return (
      l.includes("parthenium") ||
      l.includes("cyperus") ||
      l.includes("sedge") ||
      l.includes("motha") ||
      l.includes("striga")
    );
  });
  const slashMulchWeeds = selectedWeeds.filter((w) => !invasiveWeeds.includes(w));

  // Seed Requirement Output
  const seedRequirement = calculateSeedRequirement({
    areaAcres: acres,
    rowSpacingInches: rowSpacingInches,
    plantSpacingInches: plantSpacingInches,
    germinationRate: germinationPercent / 100,
    purityRate: purityPercent / 100,
    seedWeightGramsPerThousand: seedWeightGramsThousand,
  });

  // Crop Yield & Net Margin Output
  const economics = calculateCropYieldAndNetMargin({
    areaAcres: acres,
    expectedYieldPerAcreQtl: expectedYieldQtlAc,
    sellingPricePerQtl: sellingPriceQtl,
    costOfCultivationPerAcre: costOfCultivationAc,
  });

  // Handle Calculate click
  const handleCalculate = () => {
    setIsCalculating(true);
    setTimeout(() => {
      setIsCalculating(false);
      setHasCalculated(true);
      if (resultsRef.current) {
        resultsRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }, 300);
  };

  // Handle Reset click
  const handleReset = () => {
    setHasCalculated(false);
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  // Audio Speech Synthesis
  const handleToggleSpeak = () => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const textToRead = `Precision Agronomy and Economic Plan for ${currentCropObj.name} across ${fieldSize} ${fieldUnit}.
      Pillar 1: Seed Requirement. You need approximately ${seedRequirement.totalPlants.toLocaleString()} target plants and ${seedRequirement.totalSeeds.toLocaleString()} seeds, totaling ${seedRequirement.totalWeightKg} kilograms of seed.
      Pillar 2: Crop Yield and Net Margin. Expected total harvest is ${economics.totalProductionQtl} quintals or ${economics.totalProductionTonnes} tonnes. Estimated gross revenue is rupees ${economics.grossRevenue.toLocaleString()}. After total cultivation costs of rupees ${economics.totalCost.toLocaleString()}, your projected net margin is rupees ${economics.netMargin.toLocaleString()}, which is rupees ${economics.netMarginPerAcre.toLocaleString()} profit per acre with an ROI of ${economics.roiPercent} percent.
      Pillar 3: Nutrients. Recommended pure nutrients: Nitrogen ${adjustedN.toFixed(1)} kilograms, Phosphate ${adjustedP.toFixed(1)} kilograms, and Potash ${adjustedK.toFixed(1)} kilograms. Commercial fertilizers: ${ureaBags} bags of Urea, ${dapBags} bags of DAP, and ${mopBags} bags of MOP. Application method: ${applicationMethodTitle}.
      Weed strategy: ${
        isSummerSeason
          ? "Summer heat alert: Avoid complete bare clean-weeding! Keep 0 to 15 centimeters root zone clean, and slash inter-row weeds as green surface mulch to lower soil temperature by 4 to 8 degrees Celsius."
          : "Keep the root zone weed-free during the Critical Period of Weed Control."
      }`;

    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.rate = 0.95;
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
    setIsSpeaking(true);
  };

  const toggleWeedType = (label: string) => {
    if (selectedWeeds.includes(label)) {
      setSelectedWeeds(selectedWeeds.filter((w) => w !== label));
    } else {
      setSelectedWeeds([...selectedWeeds, label]);
    }
  };

  return (
    <div className="farming-calc-page w-full max-w-4xl mx-auto px-2 sm:px-4 md:px-6 py-4 sm:py-6 font-sans">
      {/* ── Top Header Navigation ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 sm:mb-6 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-start sm:items-center gap-2.5 sm:gap-3">
          <a
            href="/crops/calculator/"
            onClick={(e) => {
              if (typeof window !== "undefined" && window.history.length > 1) {
                e.preventDefault();
                window.history.back();
              }
            }}
            className="btn-21st btn-21st-secondary btn-21st-pill w-9 h-9 sm:w-10 sm:h-10 p-0 flex items-center justify-center shrink-0 cursor-pointer transition-all active:scale-95"
            title="Back to home"
            aria-label="Back to home"
          >
            <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5" />
          </a>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
              <span className="text-lg sm:text-2xl">{currentCropObj.emoji}</span>
              <h1 className="text-lg sm:text-2xl font-black tracking-tight text-slate-900 dark:text-white truncate">
                Farming Calculator
              </h1>
              <span className="text-[10px] sm:text-xs font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300 whitespace-nowrap">
                Precision Agronomist
              </span>
            </div>
            <p className="text-[11px] sm:text-xs md:text-sm text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-1 sm:line-clamp-none">
              Seed Requirements · Crop Yield & Net Margin · Precision Nutrients & Microclimate
            </p>
          </div>
        </div>

        {hasCalculated && (
          <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
            <button
              type="button"
              onClick={handleToggleSpeak}
              className={`btn-21st btn-21st-pill btn-21st-xs font-bold transition-all cursor-pointer active:scale-95 ${
                isSpeaking ? "btn-21st-primary animate-pulse" : "btn-21st-secondary"
              }`}
              title="Listen to agronomic advisory"
            >
              {isSpeaking ? (
                <VolumeX className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
              ) : (
                <Volume2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-blue-600 dark:text-blue-400" />
              )}
              <span>{isSpeaking ? "Mute" : "Listen"}</span>
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="btn-21st btn-21st-secondary btn-21st-pill btn-21st-xs font-bold transition-all cursor-pointer active:scale-95"
              title="Reset inputs"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>
        )}
      </div>

      {/* ── Calculator Form Card ── */}
      <div className="farming-card rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-7 mb-6 sm:mb-8">
        <div className="flex flex-col xs:flex-row xs:items-center justify-between gap-2 mb-4 sm:mb-5">
          <h2 className="text-sm sm:text-base md:text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Layers className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600 dark:text-blue-400 shrink-0" />
            <span>Field & Agronomic Parameters</span>
          </h2>

          <button
            type="button"
            onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
            className={`btn-21st btn-21st-pill btn-21st-xs font-bold transition-all cursor-pointer active:scale-95 self-start xs:self-auto ${
              showAdvancedSettings ? "btn-21st-primary" : "btn-21st-secondary"
            }`}
          >
            <Settings2 className="w-3.5 h-3.5 shrink-0" />
            <span>{showAdvancedSettings ? "Hide Custom Spacing & Economics" : "Customize Spacing & Economics"}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          {/* 1. Target Crop */}
          <div className="relative" ref={dropdownRef}>
            <label className="block text-[11px] sm:text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
              1. Target Crop
            </label>
            <button
              type="button"
              onClick={() => setIsCropDropdownOpen(!isCropDropdownOpen)}
              className="btn-21st btn-21st-secondary w-full justify-between p-2.5 sm:p-3 rounded-xl sm:rounded-2xl cursor-pointer hover:border-blue-500 transition-all text-left shadow-2xs"
            >
              <div className="flex items-center gap-2 min-w-0">
                <span className="text-lg sm:text-xl shrink-0">{currentCropObj.emoji}</span>
                <span className="font-bold text-xs sm:text-sm truncate">
                  {currentCropObj.name}
                </span>
                <span className="text-[11px] opacity-70 font-normal truncate hidden xs:inline">
                  ({currentCropObj.category})
                </span>
              </div>
              <ChevronDown className="w-4 h-4 opacity-70 shrink-0 ml-1" />
            </button>

            {isCropDropdownOpen && (
              <div className="absolute z-30 mt-2 w-full farming-dropdown-menu rounded-2xl shadow-2xl overflow-hidden max-h-72 flex flex-col">
                <div className="p-2 border-b border-slate-100 dark:border-slate-700/60 sticky top-0 farming-dropdown-header">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search crop..."
                      value={cropSearch}
                      onChange={(e) => setCropSearch(e.target.value)}
                      className="w-full pl-9 pr-3 py-1.5 text-xs sm:text-sm farming-input rounded-xl focus:outline-none focus:border-blue-500"
                      autoFocus
                    />
                  </div>
                  <div className="flex items-center justify-between mt-1.5 px-1 text-[10px] text-slate-400 dark:text-slate-500">
                    <span>{filteredCrops.length} targeted crops</span>
                    <span>Search by name or category</span>
                  </div>
                </div>
                <div className="overflow-y-auto p-1 divide-y divide-slate-100 dark:divide-slate-700/40 max-h-64">
                  {filteredCrops.map((c) => (
                    <button
                      key={c.name}
                      type="button"
                      onClick={() => handleCropSelect(c.name)}
                      className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-blue-50 dark:hover:bg-slate-700/60 transition-colors rounded-xl cursor-pointer"
                    >
                      <div className="flex items-center gap-2.5 truncate">
                        <span className="text-base shrink-0">{c.emoji}</span>
                        <div className="truncate">
                          <span className="text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-100 truncate block">
                            {c.name}
                          </span>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500 block truncate">
                            N-P-K: {c.n}-{c.p}-{c.k} kg/ha · {c.defaultYieldPerAcreQtl} Qtl/ac
                          </span>
                        </div>
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-semibold shrink-0 ml-2">
                        {c.category}
                      </span>
                    </button>
                  ))}
                  {filteredCrops.length === 0 && (
                    <div className="py-6 text-center text-xs text-slate-400">
                      No matching targeted crops found.
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Quick-tap crop pills */}
            <div className="flex flex-wrap gap-1 sm:gap-1.5 mt-2">
              {QUICK_TARGET_CROPS.map((cropName) => {
                const c = COMMON_CROPS.find((cr) => cr.name === cropName);
                if (!c) return null;
                const isSelected = selectedCrop === c.name;
                return (
                  <button
                    key={c.name}
                    type="button"
                    onClick={() => handleCropSelect(c.name)}
                    className={`btn-21st btn-21st-pill btn-21st-xs font-bold transition-all cursor-pointer active:scale-95 ${
                      isSelected ? "btn-21st-primary shadow-xs" : "btn-21st-secondary"
                    }`}
                  >
                    <span>{c.emoji}</span>
                    <span>{c.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 2. Field Size & Unit */}
          <div>
            <label className="block text-[11px] sm:text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
              2. Field Size & Unit
            </label>
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 mb-2">
              {/* Numeric stepper */}
              <div className="flex-1 flex items-center justify-between bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl sm:rounded-2xl p-1 shadow-2xs">
                <button
                  type="button"
                  onClick={() => setFieldSize(Math.max(0.1, Number((fieldSize - 0.5).toFixed(1))))}
                  className="btn-21st btn-21st-secondary rounded-lg sm:rounded-xl w-8 h-8 sm:w-9 sm:h-9 p-0 flex items-center justify-center shrink-0 cursor-pointer active:scale-90"
                  title="Decrease field size"
                  aria-label="Decrease field size"
                >
                  <Minus className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                </button>
                <input
                  type="number"
                  step="0.1"
                  min="0.05"
                  inputMode="decimal"
                  value={fieldSize}
                  onChange={(e) => setFieldSize(Math.max(0.01, parseFloat(e.target.value) || 0))}
                  className="w-full text-center font-black text-base sm:text-lg text-slate-900 dark:text-white bg-transparent focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => setFieldSize(Number((fieldSize + 0.5).toFixed(1)))}
                  className="btn-21st btn-21st-secondary rounded-lg sm:rounded-xl w-8 h-8 sm:w-9 sm:h-9 p-0 flex items-center justify-center shrink-0 cursor-pointer active:scale-90"
                  title="Increase field size"
                  aria-label="Increase field size"
                >
                  <Plus className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                </button>
              </div>

              {/* Units segmented toggle */}
              <div className="flex bg-slate-100 dark:bg-slate-800/90 p-1 rounded-xl sm:rounded-2xl border border-slate-200 dark:border-slate-700 justify-center gap-1 shadow-2xs">
                {(["Acre", "Hectare", "Gunta"] as const).map((unit) => {
                  const isSelected = fieldUnit === unit;
                  return (
                    <button
                      key={unit}
                      type="button"
                      onClick={() => setFieldUnit(unit)}
                      className={`btn-21st btn-21st-pill btn-21st-xs font-bold transition-all cursor-pointer ${
                        isSelected ? "btn-21st-primary shadow-xs" : "btn-21st-secondary"
                      }`}
                    >
                      {unit}
                    </button>
                  );
                })}
              </div>
            </div>
            <div className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
              ≈ {acres.toFixed(2)} Acres · {hectares.toFixed(2)} Ha · {guntas.toFixed(1)} Guntas
            </div>
          </div>

          {/* 3. Season */}
          <div>
            <label className="block text-[11px] sm:text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
              3. Season
            </label>
            <div className="grid grid-cols-3 gap-1.5 sm:gap-2">
              {SEASONS.map((s) => {
                const Icon = s.icon;
                const isSel = season === s.id;
                return (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => setSeason(s.id)}
                    className={`btn-21st farming-season-btn p-2 sm:p-2.5 rounded-xl sm:rounded-2xl text-left flex flex-col justify-between transition-all cursor-pointer ${
                      isSel
                        ? s.id === "Summer"
                          ? "farming-season-active-summer"
                          : "btn-21st-primary shadow-xs"
                        : "btn-21st-secondary"
                    }`}
                  >
                    <div className="w-full flex items-center justify-between mb-1">
                      <Icon
                        className={`w-3.5 h-3.5 sm:w-4 sm:h-4 ${
                          isSel ? (s.id === "Summer" ? "text-amber-200" : "text-white") : "text-slate-500 dark:text-slate-400"
                        }`}
                      />
                      {isSel && (
                        <div
                          className={`w-1.5 h-1.5 rounded-full ${
                            s.id === "Summer" ? "bg-amber-200" : "bg-emerald-400"
                          }`}
                        />
                      )}
                    </div>
                    <span className="text-[11px] sm:text-xs font-bold leading-tight truncate">{s.label}</span>
                  </button>
                );
              })}
            </div>
            {season === "Summer" && (
              <p className="text-[11px] sm:text-xs text-amber-600 dark:text-amber-400 font-medium mt-1.5 flex items-center gap-1">
                <ThermometerSun className="w-3.5 h-3.5 inline shrink-0" />
                <span>Microclimate preservation active: balances heat stress & evaporation.</span>
              </p>
            )}
          </div>

          {/* 4. Soil Type & 5. Irrigation */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] sm:text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
                4. Soil Type
              </label>
              <select
                value={soilType}
                onChange={(e) => setSoilType(e.target.value)}
                className="w-full p-2.5 text-xs sm:text-sm font-semibold bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl sm:rounded-2xl text-slate-900 dark:text-white focus:outline-none focus:border-blue-500"
              >
                {SOIL_TYPES.map((st) => (
                  <option key={st} value={st}>
                    {st}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[11px] sm:text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
                5. Irrigation Status
              </label>
              <select
                value={irrigationStatus}
                onChange={(e) => setIrrigationStatus(e.target.value)}
                className="w-full p-2.5 text-xs sm:text-sm font-semibold bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl sm:rounded-2xl text-slate-900 dark:text-white focus:outline-none focus:border-blue-500"
              >
                {IRRIGATION_STATUSES.map((ir) => (
                  <option key={ir} value={ir}>
                    {ir}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* 6. Weed Pressure */}
          <div className="md:col-span-2">
            <div className="flex flex-col xs:flex-row xs:items-center justify-between gap-1 mb-2">
              <label className="text-[11px] sm:text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300">
                6. Weed Pressure & Ground Cover
              </label>
              <span className="text-[11px] sm:text-xs text-blue-600 dark:text-blue-400 font-semibold">
                Rule A: Nutrient Steal Adjustment
              </span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-2.5">
              {WEED_PRESSURES.map((wp) => {
                const isSel = weedPressure === wp.label;
                return (
                  <button
                    key={wp.id}
                    type="button"
                    onClick={() => setWeedPressure(wp.label)}
                    className={`btn-21st farming-weed-pressure-btn p-2.5 sm:p-3 rounded-xl sm:rounded-2xl text-left transition-all relative overflow-hidden cursor-pointer ${
                      isSel
                        ? wp.id === "severe"
                          ? "farming-weed-pressure-severe shadow-xs"
                          : wp.id === "moderate"
                          ? "farming-weed-pressure-moderate shadow-xs"
                          : "btn-21st-primary shadow-xs"
                        : "btn-21st-secondary"
                    }`}
                  >
                    <div className="w-full">
                      <div className="text-[11px] sm:text-xs font-bold mb-0.5 sm:mb-1 truncate">{wp.label}</div>
                      <div className="text-[10px] sm:text-[11px] opacity-80 font-medium truncate">
                        {wp.buffer > 0 ? `+${wp.buffer}% Buffer` : "Optimal Baseline"}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 7. Weed Types Present */}
          <div className="md:col-span-2">
            <label className="block text-[11px] sm:text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-1.5">
              7. Weed Types Present (Select all found in field)
            </label>
            <div className="flex flex-wrap gap-1.5 sm:gap-2">
              {AVAILABLE_WEED_TYPES.map((wt) => {
                const isChecked = selectedWeeds.includes(wt.label);
                return (
                  <button
                    key={wt.id}
                    type="button"
                    onClick={() => toggleWeedType(wt.label)}
                    className={`btn-21st btn-21st-pill btn-21st-xs font-bold transition-all cursor-pointer select-none active:scale-95 ${
                      isChecked
                        ? wt.isInvasive
                          ? "farming-weed-chip-invasive-active shadow-xs"
                          : "btn-21st-primary shadow-xs"
                        : "btn-21st-secondary"
                    }`}
                  >
                    <div
                      className={`w-3.5 h-3.5 rounded-full flex items-center justify-center text-[10px] shrink-0 ${
                        isChecked
                          ? "bg-white/25 text-white"
                          : "border border-slate-400 dark:border-slate-500"
                      }`}
                    >
                      {isChecked && <CheckCircle2 className="w-3 h-3 text-white" />}
                    </div>
                    <span className="truncate">{wt.label}</span>
                    {wt.isInvasive && (
                      <span
                        className={`text-[9px] px-1.5 py-0.5 rounded-full uppercase font-black tracking-tight shrink-0 ${
                          isChecked
                            ? "bg-white/25 text-white"
                            : "farming-weed-invasive-badge"
                        }`}
                      >
                        Invasive
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* ── Optional Customizable Parameters: Seed Spacing & Net Margin Economics ── */}
          {showAdvancedSettings && (
            <div className="md:col-span-2 p-3.5 sm:p-4 rounded-xl sm:rounded-2xl bg-blue-50/50 dark:bg-slate-800/50 border border-blue-200 dark:border-slate-700 space-y-4">
              <div>
                <h4 className="text-xs font-black uppercase tracking-wider text-blue-900 dark:text-blue-300 mb-2.5 flex items-center gap-1.5">
                  <Scale className="w-3.5 h-3.5" />
                  <span>Seed Requirement & Plant Spacing Parameters</span>
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2.5 sm:gap-3">
                  <div>
                    <label className="block text-[10px] sm:text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">
                      Row Spacing (in)
                    </label>
                    <input
                      type="number"
                      step="1"
                      min="1"
                      inputMode="decimal"
                      value={rowSpacingInches}
                      onChange={(e) => setRowSpacingInches(Math.max(1, parseFloat(e.target.value) || 1))}
                      className="w-full p-2 text-xs font-bold rounded-xl farming-input"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] sm:text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">
                      Plant Spacing (in)
                    </label>
                    <input
                      type="number"
                      step="1"
                      min="1"
                      inputMode="decimal"
                      value={plantSpacingInches}
                      onChange={(e) => setPlantSpacingInches(Math.max(1, parseFloat(e.target.value) || 1))}
                      className="w-full p-2 text-xs font-bold rounded-xl farming-input"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] sm:text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">
                      Germination (%)
                    </label>
                    <input
                      type="number"
                      step="1"
                      min="50"
                      max="100"
                      inputMode="decimal"
                      value={germinationPercent}
                      onChange={(e) => setGerminationPercent(Math.min(100, Math.max(10, parseFloat(e.target.value) || 90)))}
                      className="w-full p-2 text-xs font-bold rounded-xl farming-input"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] sm:text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">
                      Purity Rate (%)
                    </label>
                    <input
                      type="number"
                      step="1"
                      min="50"
                      max="100"
                      inputMode="decimal"
                      value={purityPercent}
                      onChange={(e) => setPurityPercent(Math.min(100, Math.max(10, parseFloat(e.target.value) || 98)))}
                      className="w-full p-2 text-xs font-bold rounded-xl farming-input"
                    />
                  </div>
                  <div className="col-span-2 sm:col-span-1">
                    <label className="block text-[10px] sm:text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">
                      1000 Seed Wt (g)
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      min="0.1"
                      inputMode="decimal"
                      value={seedWeightGramsThousand}
                      onChange={(e) => setSeedWeightGramsThousand(Math.max(0.1, parseFloat(e.target.value) || 40))}
                      className="w-full p-2 text-xs font-bold rounded-xl farming-input"
                    />
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-200 dark:border-slate-700">
                <h4 className="text-xs font-black uppercase tracking-wider text-emerald-900 dark:text-emerald-300 mb-2.5 flex items-center gap-1.5">
                  <Coins className="w-3.5 h-3.5" />
                  <span>Crop Yield & Net Margin Parameters</span>
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 sm:gap-3">
                  <div>
                    <label className="block text-[10px] sm:text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">
                      Expected Yield (Quintals/acre)
                    </label>
                    <input
                      type="number"
                      step="1"
                      min="1"
                      inputMode="decimal"
                      value={expectedYieldQtlAc}
                      onChange={(e) => setExpectedYieldQtlAc(Math.max(0.1, parseFloat(e.target.value) || 1))}
                      className="w-full p-2 text-xs font-bold rounded-xl farming-input"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] sm:text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">
                      Selling Price / MSP (₹/Quintal)
                    </label>
                    <input
                      type="number"
                      step="25"
                      min="100"
                      inputMode="decimal"
                      value={sellingPriceQtl}
                      onChange={(e) => setSellingPriceQtl(Math.max(1, parseFloat(e.target.value) || 1))}
                      className="w-full p-2 text-xs font-bold rounded-xl farming-input"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] sm:text-[11px] font-bold text-slate-600 dark:text-slate-300 mb-1">
                      Cost of Cultivation (₹/acre)
                    </label>
                    <input
                      type="number"
                      step="500"
                      min="1000"
                      inputMode="decimal"
                      value={costOfCultivationAc}
                      onChange={(e) => setCostOfCultivationAc(Math.max(1, parseFloat(e.target.value) || 1))}
                      className="w-full p-2 text-xs font-bold rounded-xl farming-input"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ── Action Button ── */}
        <div className="mt-5 sm:mt-7 pt-4 border-t border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 text-center sm:text-left">
            Calculates seed requirements, crop yield, net profit margins, and precision nutrient buffers simultaneously.
          </p>

          <button
            type="button"
            onClick={handleCalculate}
            disabled={isCalculating}
            className="btn-21st btn-21st-primary btn-21st-pill w-full sm:w-auto px-7 sm:px-8 py-3.5 text-xs sm:text-sm font-black shadow-lg shadow-blue-500/25 flex items-center justify-center gap-2.5 transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
          >
            {isCalculating ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span className="text-white font-black">Evaluating Full Farm Model…</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-white" />
                <span className="text-white font-black">Calculate Precision Plan</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* ── CALCULATED STRUCTURED OUTPUT SECTIONS ── */}
      {hasCalculated && (
        <div ref={resultsRef} className="space-y-4 sm:space-y-6 animate-in fade-in duration-300">
          {/* Header Summary Banner */}
          <div className="bg-gradient-to-r from-blue-700 via-indigo-700 to-sky-700 text-white rounded-2xl sm:rounded-3xl p-4 sm:p-5 md:p-6 shadow-xl">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/20 text-xs font-semibold backdrop-blur-sm mb-2">
                  <span>{currentCropObj.emoji}</span>
                  <span>{currentCropObj.name} Decision Support</span>
                  <span>·</span>
                  <span>{season}</span>
                </div>
                <h2 className="text-lg sm:text-xl md:text-2xl font-black">
                  Farming Decision & Net Margin Assessment
                </h2>
                <p className="text-xs sm:text-sm text-blue-100 mt-1 max-w-xl">
                  Formulated for {fieldSize} {fieldUnit} ({acres.toFixed(2)} Acres / {hectares.toFixed(2)} Ha) on{" "}
                  {soilType} soil with {irrigationStatus} irrigation.
                </p>
              </div>

              <div className="grid grid-cols-2 sm:flex sm:items-center gap-2 sm:gap-3 w-full sm:w-auto">
                {weedLossPenaltyPct > 0 && (
                  <div className="bg-white/10 backdrop-blur-md rounded-xl sm:rounded-2xl p-2.5 sm:p-3 border border-white/20 text-left sm:text-right">
                    <div className="text-[10px] sm:text-[11px] text-blue-100 font-medium truncate">Weed Loss Risk</div>
                    <div className="text-base sm:text-lg font-black text-amber-300">~{weedLossPenaltyPct}% Steal</div>
                    <div className="text-[10px] sm:text-[11px] text-blue-200">+{bufferPercent}% Buffer</div>
                  </div>
                )}
                <div className="bg-white/10 backdrop-blur-md rounded-xl sm:rounded-2xl p-2.5 sm:p-3 border border-white/20 text-left sm:text-right">
                  <div className="text-[10px] sm:text-[11px] text-blue-100 font-medium truncate">Estimated Net Margin</div>
                  <div className="text-base sm:text-xl font-black text-emerald-300 truncate">
                    ₹{economics.netMargin.toLocaleString()}
                  </div>
                  <div className="text-[10px] sm:text-[11px] text-blue-200">ROI: +{economics.roiPercent}%</div>
                </div>
              </div>
            </div>
          </div>

          {/* ── Navigation Tab Switcher ── */}
          <div className="flex bg-slate-100 dark:bg-slate-800 p-1 sm:p-1.5 rounded-xl sm:rounded-2xl border border-slate-200 dark:border-slate-700 overflow-x-auto no-scrollbar scroll-smooth gap-1 sm:gap-1.5">
            <button
              type="button"
              onClick={() => setActiveTab("all")}
              className={`btn-21st btn-21st-pill btn-21st-xs font-bold whitespace-nowrap transition-all cursor-pointer ${
                activeTab === "all" ? "btn-21st-primary shadow-xs" : "btn-21st-secondary"
              }`}
            >
              All Sections
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("seed")}
              className={`btn-21st btn-21st-pill btn-21st-xs font-bold whitespace-nowrap transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                activeTab === "seed" ? "btn-21st-primary shadow-xs" : "btn-21st-secondary"
              }`}
            >
              <Scale className="w-3.5 h-3.5 shrink-0" />
              <span>Seed Requirement</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("economics")}
              className={`btn-21st btn-21st-pill btn-21st-xs font-bold whitespace-nowrap transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                activeTab === "economics" ? "btn-21st-primary shadow-xs" : "btn-21st-secondary"
              }`}
            >
              <Coins className="w-3.5 h-3.5 shrink-0" />
              <span>Yield & Net Margin</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("nutrition")}
              className={`btn-21st btn-21st-pill btn-21st-xs font-bold whitespace-nowrap transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                activeTab === "nutrition" ? "btn-21st-primary shadow-xs" : "btn-21st-secondary"
              }`}
            >
              <Droplets className="w-3.5 h-3.5 shrink-0" />
              <span>Nutrients & Weeding</span>
            </button>
          </div>

          {/* ════════ PILLAR A: SEED REQUIREMENT CALCULATOR ════════ */}
          {(activeTab === "all" || activeTab === "seed") && (
            <div className="farming-card rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-7">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300 flex items-center justify-center font-bold text-xs sm:text-sm shrink-0">
                    🌱
                  </div>
                  <div>
                    <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                      Seed Requirement & Plant Population
                    </h3>
                    <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                      Calculated using crop spacing ({rowSpacingInches}&Prime; &times; {plantSpacingInches}&Prime;), {germinationPercent}% germination, and {purityPercent}% seed purity.
                    </p>
                  </div>
                </div>
              </div>

              {/* Stat Cards for Seed Requirements */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-3.5 mb-4 sm:mb-5">
                <div className="farming-stat-card farming-stat-purple rounded-xl sm:rounded-2xl p-3.5 sm:p-4">
                  <div className="text-[11px] sm:text-xs font-bold farming-stat-label-purple mb-1">
                    TOTAL WEIGHT NEEDED
                  </div>
                  <div className="text-2xl sm:text-3xl font-black farming-stat-value truncate">
                    {seedRequirement.totalWeightKg} <span className="text-xs sm:text-sm font-semibold opacity-75">kg</span>
                  </div>
                  <div className="text-[10px] sm:text-xs farming-stat-sub-purple mt-1.5 font-medium">
                    Test Weight: {seedWeightGramsThousand}g per 1000 seeds
                  </div>
                </div>

                <div className="farming-stat-card rounded-xl sm:rounded-2xl p-3.5 sm:p-4">
                  <div className="text-[11px] sm:text-xs font-bold farming-stat-label mb-1">
                    TARGET PLANT COUNT
                  </div>
                  <div className="text-2xl sm:text-3xl font-black farming-stat-value truncate">
                    {seedRequirement.totalPlants.toLocaleString()}
                  </div>
                  <div className="text-[10px] sm:text-xs farming-stat-sub mt-1.5 font-medium">
                    Target population for {acres.toFixed(2)} acres
                  </div>
                </div>

                <div className="farming-stat-card rounded-xl sm:rounded-2xl p-3.5 sm:p-4">
                  <div className="text-[11px] sm:text-xs font-bold farming-stat-label mb-1">
                    TOTAL SEEDS TO SOW
                  </div>
                  <div className="text-2xl sm:text-3xl font-black farming-stat-value truncate">
                    {seedRequirement.totalSeeds.toLocaleString()}
                  </div>
                  <div className="text-[10px] sm:text-xs farming-stat-sub mt-1.5 font-medium">
                    Includes {100 - germinationPercent}% buffer for emergence
                  </div>
                </div>
              </div>

              {/* Spacing Details Bar */}
              <div className="p-3 sm:p-3.5 rounded-xl sm:rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs">
                <div className="flex flex-wrap items-center gap-3 sm:gap-4">
                  <div>
                    <span className="text-slate-400 font-medium">Row Spacing:</span>{" "}
                    <strong className="text-slate-800 dark:text-slate-200">{rowSpacingInches} inches</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium">Plant Spacing:</span>{" "}
                    <strong className="text-slate-800 dark:text-slate-200">{plantSpacingInches} inches</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 font-medium">Area per Plant:</span>{" "}
                    <strong className="text-slate-800 dark:text-slate-200">
                      {(rowSpacingInches * plantSpacingInches).toFixed(0)} sq inches
                    </strong>
                  </div>
                </div>
                <div className="text-slate-500 dark:text-slate-400 font-medium text-[11px] sm:text-xs">
                  Formula: Target Plants / (Germination &times; Purity) &times; Test Weight
                </div>
              </div>
            </div>
          )}

          {/* ════════ PILLAR B: CROP YIELD & NET MARGIN ════════ */}
          {(activeTab === "all" || activeTab === "economics") && (
            <div className="farming-card rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-7">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 flex items-center justify-center font-bold text-xs sm:text-sm shrink-0">
                    💰
                  </div>
                  <div>
                    <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                      Crop Yield & Net Margin Analysis
                    </h3>
                    <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                      Financial forecast based on {expectedYieldQtlAc} Qtl/ac harvest and ₹{sellingPriceQtl}/Qtl market price.
                    </p>
                  </div>
                </div>
                <div className="self-start sm:self-auto">
                  <span className="inline-flex items-center gap-1 text-[11px] sm:text-xs font-black px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300">
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span>+{economics.roiPercent}% Return on Cost</span>
                  </span>
                </div>
              </div>

              {/* Economic KPI Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3.5 mb-4 sm:mb-5">
                <div className="farming-stat-card rounded-xl sm:rounded-2xl p-3 sm:p-4">
                  <div className="text-[10px] sm:text-xs font-bold farming-stat-label mb-1 truncate">
                    EXPECTED HARVEST
                  </div>
                  <div className="text-lg xs:text-xl sm:text-2xl font-black farming-stat-value truncate">
                    {economics.totalProductionQtl} <span className="text-[11px] sm:text-xs font-semibold opacity-70">Qtl</span>
                  </div>
                  <div className="text-[10px] sm:text-[11px] farming-stat-sub mt-1 truncate">
                    ≈ {economics.totalProductionTonnes} Tonnes
                  </div>
                </div>

                <div className="farming-stat-card rounded-xl sm:rounded-2xl p-3 sm:p-4">
                  <div className="text-[10px] sm:text-xs font-bold farming-stat-label mb-1 truncate">
                    GROSS REVENUE
                  </div>
                  <div className="text-lg xs:text-xl sm:text-2xl font-black text-blue-600 dark:text-blue-400 truncate" title={`₹${economics.grossRevenue.toLocaleString()}`}>
                    ₹{economics.grossRevenue.toLocaleString()}
                  </div>
                  <div className="text-[10px] sm:text-[11px] farming-stat-sub mt-1 truncate">
                    At ₹{sellingPriceQtl}/Qtl
                  </div>
                </div>

                <div className="farming-stat-card rounded-xl sm:rounded-2xl p-3 sm:p-4">
                  <div className="text-[10px] sm:text-xs font-bold farming-stat-label mb-1 truncate">
                    ESTIMATED COSTS
                  </div>
                  <div className="text-lg xs:text-xl sm:text-2xl font-black text-amber-600 dark:text-amber-400 truncate" title={`₹${economics.totalCost.toLocaleString()}`}>
                    ₹{economics.totalCost.toLocaleString()}
                  </div>
                  <div className="text-[10px] sm:text-[11px] farming-stat-sub mt-1 truncate">
                    ₹{costOfCultivationAc.toLocaleString()}/ac
                  </div>
                </div>

                <div className="farming-stat-card farming-stat-profit rounded-xl sm:rounded-2xl p-3 sm:p-4">
                  <div className="text-[10px] sm:text-xs font-black farming-stat-label-profit mb-1 truncate">
                    PROJECTED NET PROFIT
                  </div>
                  <div className="text-lg xs:text-xl sm:text-2xl font-black farming-stat-profit-val truncate" title={`₹${economics.netMargin.toLocaleString()}`}>
                    ₹{economics.netMargin.toLocaleString()}
                  </div>
                  <div className="text-[10px] sm:text-[11px] font-bold farming-stat-sub-profit mt-1 truncate">
                    ₹{economics.netMarginPerAcre.toLocaleString()}/ac
                  </div>
                </div>
              </div>

              {/* Benefit-Cost Ratio Bar */}
              <div className="p-3 sm:p-3.5 rounded-xl sm:rounded-2xl bg-emerald-50/50 dark:bg-slate-800/60 border border-emerald-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                  <Coins className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span className="font-bold text-slate-800 dark:text-slate-200">
                    Benefit-Cost Ratio (BCR): {economics.benefitCostRatio}x
                  </span>
                  <span className="text-slate-400 hidden xs:inline">|</span>
                  <span className="text-slate-600 dark:text-slate-300 text-[11px] sm:text-xs">
                    For every ₹1 invested, the farm produces ₹{economics.benefitCostRatio} in revenue.
                  </span>
                </div>
                <div className="text-slate-500 dark:text-slate-400 text-[10px] sm:text-[11px]">
                  Net Margin = Gross Revenue &minus; Cultivation Costs
                </div>
              </div>
            </div>
          )}

          {/* ════════ PILLAR C: PRECISION NUTRIENTS & WEED MANAGEMENT ════════ */}
          {(activeTab === "all" || activeTab === "nutrition") && (
            <div className="space-y-4 sm:space-y-6">
              {/* Section 1: Quantitative Input Adjustments */}
              <div className="farming-card rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-7">
                <div className="flex items-center gap-2.5 mb-4">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 flex items-center justify-center font-bold text-xs sm:text-sm shrink-0">
                    1
                  </div>
                  <div>
                    <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                      Section 1: Quantitative Input Adjustments
                    </h3>
                    <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                      Adjusted N-P-K amounts and specific placement method based on field area and weed pressure.
                    </p>
                  </div>
                </div>

                {/* Nutrients Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-3.5 mb-4 sm:mb-5">
                  {/* Nitrogen */}
                  <div className="farming-stat-card rounded-xl sm:rounded-2xl p-3.5 sm:p-4">
                    <div className="flex items-center justify-between text-xs font-bold farming-stat-label mb-1">
                      <span>NITROGEN (N)</span>
                      <span className="text-[10px] sm:text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                        +{bufferPercent}% Buffer
                      </span>
                    </div>
                    <div className="text-xl sm:text-2xl font-black farming-stat-value">
                      {adjustedN.toFixed(1)} <span className="text-xs font-medium opacity-70">kg pure N</span>
                    </div>
                    <div className="text-xs farming-stat-sub mt-2 pt-2 border-t border-slate-200 dark:border-slate-700/80 flex items-center justify-between">
                      <span>Urea (46% N):</span>
                      <span className="font-bold text-blue-600 dark:text-blue-400">{ureaBags} bags (50kg)</span>
                    </div>
                  </div>

                  {/* Phosphorus */}
                  <div className="farming-stat-card rounded-xl sm:rounded-2xl p-3.5 sm:p-4">
                    <div className="flex items-center justify-between text-xs font-bold farming-stat-label mb-1">
                      <span>PHOSPHORUS (P₂O₅)</span>
                      <span className="text-[10px] sm:text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                        +{bufferPercent}% Buffer
                      </span>
                    </div>
                    <div className="text-xl sm:text-2xl font-black farming-stat-value">
                      {adjustedP.toFixed(1)} <span className="text-xs font-medium opacity-70">kg pure P₂O₅</span>
                    </div>
                    <div className="text-xs farming-stat-sub mt-2 pt-2 border-t border-slate-200 dark:border-slate-700/80 flex items-center justify-between">
                      <span>DAP (18-46-0):</span>
                      <span className="font-bold text-blue-600 dark:text-blue-400">{dapBags} bags (50kg)</span>
                    </div>
                  </div>

                  {/* Potassium */}
                  <div className="farming-stat-card rounded-xl sm:rounded-2xl p-3.5 sm:p-4">
                    <div className="flex items-center justify-between text-xs font-bold farming-stat-label mb-1">
                      <span>POTASSIUM (K₂O)</span>
                      <span className="text-[10px] sm:text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                        +{bufferPercent}% Buffer
                      </span>
                    </div>
                    <div className="text-xl sm:text-2xl font-black farming-stat-value">
                      {adjustedK.toFixed(1)} <span className="text-xs font-medium opacity-70">kg pure K₂O</span>
                    </div>
                    <div className="text-xs farming-stat-sub mt-2 pt-2 border-t border-slate-200 dark:border-slate-700/80 flex items-center justify-between">
                      <span>MOP (60% K₂O):</span>
                      <span className="font-bold text-blue-600 dark:text-blue-400">{mopBags} bags (50kg)</span>
                    </div>
                  </div>
                </div>

                {/* Application Method Callout */}
                <div className="bg-blue-50/80 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 rounded-xl sm:rounded-2xl p-3.5 sm:p-4">
                  <div className="flex items-start gap-2.5 sm:gap-3">
                    <div className="p-1.5 sm:p-2 rounded-xl bg-blue-600 text-white shrink-0 mt-0.5">
                      <Droplets className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <div className="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-blue-800 dark:text-blue-300">
                        Mandatory Application Method
                      </div>
                      <div className="text-xs sm:text-sm font-black text-slate-900 dark:text-white mt-0.5">
                        {applicationMethodTitle}
                      </div>
                      <p className="text-[11px] sm:text-xs text-slate-700 dark:text-slate-300 mt-1 leading-relaxed">
                        {applicationMethodDetail}
                      </p>

                      <div className="grid grid-cols-3 gap-1.5 sm:gap-2 mt-3 pt-3 border-t border-blue-200/60 dark:border-blue-800/60 text-center">
                        <div className="farming-subcard rounded-lg sm:rounded-xl p-1.5 sm:p-2">
                          <div className="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 font-semibold truncate">Basal Dose</div>
                          <div className="text-xs sm:text-sm font-bold text-blue-700 dark:text-blue-300">{basalSplitPct}%</div>
                        </div>
                        <div className="farming-subcard rounded-lg sm:rounded-xl p-1.5 sm:p-2">
                          <div className="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 font-semibold truncate">Top-Dress 1</div>
                          <div className="text-xs sm:text-sm font-bold text-blue-700 dark:text-blue-300">{topdress1SplitPct}%</div>
                          <div className="text-[9px] text-slate-400 hidden xs:block">Post-Weed</div>
                        </div>
                        <div className="farming-subcard rounded-lg sm:rounded-xl p-1.5 sm:p-2">
                          <div className="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 font-semibold truncate">Top-Dress 2</div>
                          <div className="text-xs sm:text-sm font-bold text-blue-700 dark:text-blue-300">{topdress2SplitPct}%</div>
                          <div className="text-[9px] text-slate-400 hidden xs:block">Repro</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Section 2: Season-Specific Weed & Microclimate Management */}
              <div className="farming-card rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-7">
                <div className="flex items-center gap-2.5 mb-4">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 flex items-center justify-center font-bold text-xs sm:text-sm shrink-0">
                    2
                  </div>
                  <div>
                    <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                      Section 2: Season-Specific Weed & Microclimate Management
                    </h3>
                    <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                      {season} seasonal protocol: Microclimate thermal insulation vs. root weed competition.
                    </p>
                  </div>
                </div>

                {/* Summer Rule B Highlight */}
                {isSummerSeason ? (
                  <div className="border border-amber-300 dark:border-amber-700 bg-amber-50/70 dark:bg-amber-950/30 rounded-xl sm:rounded-2xl p-4 sm:p-5 mb-4 sm:mb-5">
                    <div className="flex items-start gap-2.5 sm:gap-3">
                      <div className="p-1.5 sm:p-2 rounded-xl bg-amber-500 text-white shrink-0">
                        <Sun className="w-4 h-4 sm:w-5 sm:h-5" />
                      </div>
                      <div>
                        <div className="text-[10px] sm:text-xs font-black uppercase tracking-wider text-amber-900 dark:text-amber-300">
                          Rule B: Summer Microclimate Strategy — Avoid Total Clean-Weeding!
                        </div>
                        <div className="text-xs sm:text-sm font-bold text-amber-950 dark:text-amber-100 mt-1">
                          Never recommend complete bare-soil stripping (100% clean-weeding).
                        </div>
                        <p className="text-[11px] sm:text-xs text-amber-900/90 dark:text-amber-200/90 mt-1.5 leading-relaxed">
                          <strong>Agronomic Reason:</strong> Bare soil exposed to extreme summer heat absorbs intense solar
                          radiation, forms a dry impermeable surface crust, triggers high Vapor Pressure Deficit (rapid
                          evaporation), and causes root-zone thermal shock, reducing crop yield far more than mild weed
                          presence.
                        </p>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3 mt-3 sm:mt-4">
                          {/* Root Zone */}
                          <div className="farming-subcard rounded-xl sm:rounded-2xl p-3 sm:p-3.5 border border-amber-200 dark:border-amber-800/50">
                            <div className="text-[11px] sm:text-xs font-black text-emerald-700 dark:text-emerald-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                              <CheckCircle2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" />
                              <span>Root Zone (0–15 cm)</span>
                            </div>
                            <p className="text-[11px] sm:text-xs text-slate-700 dark:text-slate-300 font-medium leading-relaxed">
                              Keep 100% clean through localized ring weeding. Eliminates direct competition for water, space,
                              and applied fertilizers.
                            </p>
                          </div>

                          {/* Inter-Row Space */}
                          <div className="farming-subcard rounded-xl sm:rounded-2xl p-3 sm:p-3.5 border border-amber-200 dark:border-amber-800/50">
                            <div className="text-[11px] sm:text-xs font-black text-blue-700 dark:text-blue-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                              <Layers className="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0" />
                              <span>Inter-Row Space (&gt;15 cm)</span>
                            </div>
                            <p className="text-[11px] sm:text-xs text-slate-700 dark:text-slate-300 font-medium leading-relaxed">
                              Do NOT uproot non-aggressive weeds! Instead, <strong>slash / mow at ground level</strong> and
                              leave biomass on the surface as <strong>green surface mulch</strong>.
                            </p>
                          </div>
                        </div>

                        {/* Quantified Benefits */}
                        <div className="mt-3 pt-3 border-t border-amber-200/80 dark:border-amber-800/60 flex flex-wrap items-center gap-1.5 sm:gap-2 text-[10px] sm:text-xs font-bold text-amber-900 dark:text-amber-200">
                          <span className="inline-flex items-center gap-1 bg-amber-200/60 dark:bg-amber-900/60 px-2 py-0.5 sm:px-2.5 sm:py-1 rounded-lg">
                            🌡️ Lowers soil temp by 4–8°C
                          </span>
                          <span className="inline-flex items-center gap-1 bg-amber-200/60 dark:bg-amber-900/60 px-2 py-0.5 sm:px-2.5 sm:py-1 rounded-lg">
                            💧 Cuts evaporation by up to 35%
                          </span>
                          <span className="inline-flex items-center gap-1 bg-amber-200/60 dark:bg-amber-900/60 px-2 py-0.5 sm:px-2.5 sm:py-1 rounded-lg">
                            🌱 Adds rich organic matter
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 rounded-xl sm:rounded-2xl p-3.5 sm:p-4 mb-4 sm:mb-5">
                    <div className="text-[10px] sm:text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1">
                      Seasonal Protocol ({season})
                    </div>
                    <p className="text-[11px] sm:text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                      Maintain clean weed-free bands in the root zone during the Critical Period of Weed Control (CPWC, Days
                      15–45). Ensure field drainage channels are cleared to prevent fungal root diseases during high moisture
                      periods.
                    </p>
                  </div>
                )}

                {/* Weeds Classification: Slash-as-Mulch vs Remove Immediately */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                  {/* Safe to Slash as Mulch */}
                  <div className="rounded-xl sm:rounded-2xl p-3.5 sm:p-4 border border-emerald-200 dark:border-emerald-800/50 bg-emerald-50/50 dark:bg-emerald-950/20">
                    <div className="text-[11px] sm:text-xs font-black text-emerald-800 dark:text-emerald-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>Weeds Suitable for Green Mulch</span>
                    </div>
                    {slashMulchWeeds.length > 0 ? (
                      <ul className="text-[11px] sm:text-xs text-slate-700 dark:text-slate-300 space-y-1.5 list-disc list-inside">
                        {slashMulchWeeds.map((w, idx) => (
                          <li key={idx} className="font-medium break-words">
                            {w}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 italic">
                        Annual non-aggressive grasses and soft broadleaf weeds may be slashed at ground level.
                      </p>
                    )}
                    <div className="text-[10px] sm:text-[11px] text-emerald-700 dark:text-emerald-400 mt-2 font-medium">
                      Slash with sickle/mower and spread evenly as a 3–5 cm blanket between crop rows.
                    </div>
                  </div>

                  {/* Noxious / Invasive to Remove Immediately */}
                  <div className="rounded-xl sm:rounded-2xl p-3.5 sm:p-4 border border-red-200 dark:border-red-800/50 bg-red-50/50 dark:bg-red-950/20">
                    <div className="text-[11px] sm:text-xs font-black text-red-800 dark:text-red-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <ShieldAlert className="w-4 h-4 text-red-600 shrink-0" />
                      <span>Must Uproot / Remove Immediately</span>
                    </div>
                    {invasiveWeeds.length > 0 ? (
                      <ul className="text-[11px] sm:text-xs text-red-900 dark:text-red-200 space-y-1.5 list-disc list-inside">
                        {invasiveWeeds.map((w, idx) => (
                          <li key={idx} className="font-semibold break-words">
                            {w}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 italic">
                        Parthenium, Cyperus rotundus (Motha), or Striga if present.
                      </p>
                    )}
                    <div className="text-[10px] sm:text-[11px] text-red-700 dark:text-red-300 mt-2 font-medium">
                      <strong>Strict Exception:</strong> Never mulch Parthenium or Cyperus tubers. They release
                      allelopathic toxins and multiply underground. Uproot manually before flowering!
                    </div>
                  </div>
                </div>
              </div>

              {/* Section 3: High-Yield Action Plan */}
              <div className="farming-card rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-7">
                <div className="flex items-center gap-2.5 mb-4 sm:mb-5">
                  <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 flex items-center justify-center font-bold text-xs sm:text-sm shrink-0">
                    3
                  </div>
                  <div>
                    <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                      Section 3: High-Yield Action Plan (Step-by-Step)
                    </h3>
                    <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                      Field operations timeline from Day 0 through peak vegetative growth.
                    </p>
                  </div>
                </div>

                <div className="space-y-3 sm:space-y-4">
                  {/* Step 1 */}
                  <div className="farming-step-card flex items-start gap-2.5 sm:gap-3.5 p-3 sm:p-3.5 rounded-xl sm:rounded-2xl">
                    <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-lg sm:rounded-xl bg-blue-600 text-white flex items-center justify-center font-black text-[11px] sm:text-xs shrink-0 mt-0.5">
                      01
                    </div>
                    <div>
                      <div className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
                        Day 0–15: Critical Root-Zone Clearance & Basal Placement
                      </div>
                      <p className="text-[11px] sm:text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
                        Perform localized ring weeding in the 0–15 cm strip around each seedling. Apply basal fertilizer (
                        {basalSplitPct}% of total) banded 5–10 cm to the side of the seed line. In summer, retain inter-row
                        slashed green mulch immediately to insulate moist soil.
                      </p>
                    </div>
                  </div>

                  {/* Step 2 */}
                  <div className="farming-step-card flex items-start gap-2.5 sm:gap-3.5 p-3 sm:p-3.5 rounded-xl sm:rounded-2xl">
                    <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-lg sm:rounded-xl bg-emerald-600 text-white flex items-center justify-center font-black text-[11px] sm:text-xs shrink-0 mt-0.5">
                      02
                    </div>
                    <div>
                      <div className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
                        Fertilizer Timing Rule: Never Apply Nitrogen Before Weeding!
                      </div>
                      <p className="text-[11px] sm:text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
                        <strong>Mandatory timing:</strong> Never apply nitrogen into weed-infested rows. Always clear or slash
                        weeds first, and apply the top-dress dose strictly <strong>24–48 hours after root-zone clearing</strong>.
                        This ensures 100% of the active nitrogen feeds the crop rather than fueling weed canopy surges.
                      </p>
                    </div>
                  </div>

                  {/* Step 3 */}
                  <div className="farming-step-card flex items-start gap-2.5 sm:gap-3.5 p-3 sm:p-3.5 rounded-xl sm:rounded-2xl">
                    <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-lg sm:rounded-xl bg-indigo-600 text-white flex items-center justify-center font-black text-[11px] sm:text-xs shrink-0 mt-0.5">
                      03
                    </div>
                    <div>
                      <div className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
                        Irrigation Guidance ({irrigationStatus.toUpperCase()})
                      </div>
                      <p className="text-[11px] sm:text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
                        {isSummerSeason
                          ? "Irrigate during early mornings (5–8 AM) or late dusk (after 6 PM) to avoid high vapor pressure evaporation. The inter-row mulch layer maintains sub-surface root moisture 35% longer, allowing you to space irrigation cycles comfortably."
                          : "Maintain consistent soil moisture at key developmental stages (flowering, pod/grain filling). Avoid standing water in heavy clay beds."}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Operational Reminder Card */}
                <div className="farming-reminder-box mt-4 sm:mt-5 p-3 sm:p-4 rounded-xl sm:rounded-2xl flex items-start gap-2.5 sm:gap-3">
                  <AlertTriangle className="w-4 h-4 sm:w-5 sm:h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="text-[10px] sm:text-xs font-black uppercase tracking-wider text-amber-900 dark:text-amber-300">
                      Operational Agronomist Reminder
                    </div>
                    <p className="text-[11px] sm:text-xs text-amber-950 dark:text-amber-100 mt-0.5 font-medium leading-relaxed">
                      Always check your local <strong>Soil Testing Report / Soil Health Card (SHC)</strong> before applying heavy
                      chemical inputs. Adjust the calculated doses downwards if your soil tests indicate high baseline residual
                      nitrogen, phosphorus, or potassium.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
