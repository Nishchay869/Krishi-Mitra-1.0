import * as React from "react";
import "./FarmingCalculator.css";
import {
  ArrowLeft,
  Volume2,
  VolumeX,
  Plus,
  Minus,
  Search,
  Sun,
  CloudRain,
  Snowflake,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
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
  // Results are computed on every render; this only reveals them and scrolls to them.
  const handleCalculate = () => {
    setHasCalculated(true);
    requestAnimationFrame(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }));
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
            className="btn-21st btn-21st-secondary btn-21st-pill w-9 h-9 sm:w-10 sm:h-10 p-0 flex items-center justify-center shrink-0 cursor-pointer transition-all"
            title="Back to home"
            aria-label="Back to home"
          >
            <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5" />
          </a>
          <div className="min-w-0">
            <h1 className="text-lg sm:text-2xl font-semibold text-slate-900 dark:text-white">
              Farming calculator
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-0.5">
              Seed, fertilizer, yield and profit for your field.
            </p>
          </div>
        </div>

        {hasCalculated && (
          <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
            <button
              type="button"
              onClick={handleToggleSpeak}
              className={`btn-21st btn-21st-pill btn-21st-xs font-bold transition-all cursor-pointer ${
                isSpeaking ? "btn-21st-primary" : "btn-21st-secondary"
              }`}
              title="Listen to agronomic advisory"
            >
              {isSpeaking ? (
                <VolumeX className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
              ) : (
                <Volume2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              )}
              <span>{isSpeaking ? "Stop" : "Listen"}</span>
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="btn-21st btn-21st-secondary btn-21st-pill btn-21st-xs font-bold transition-all cursor-pointer"
              title="Reset inputs"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          </div>
        )}
      </div>

      {/* ── Calculator Form Card ── */}
      <div className="farming-card rounded-xl p-4 sm:p-6 md:p-7 mb-6 sm:mb-8">
        <div className="flex flex-col xs:flex-row xs:items-center justify-between gap-2 mb-4 sm:mb-5">
          <h2 className="text-sm sm:text-base font-semibold text-slate-900 dark:text-white">
            Your field
          </h2>

          <button
            type="button"
            onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
            className={`btn-21st btn-21st-pill btn-21st-xs font-bold transition-all cursor-pointer self-start xs:self-auto ${
              showAdvancedSettings ? "btn-21st-primary" : "btn-21st-secondary"
            }`}
          >
            <Settings2 className="w-3.5 h-3.5 shrink-0" />
            <span>{showAdvancedSettings ? "Hide spacing & prices" : "Edit spacing & prices"}</span>
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          {/* 1. Target Crop */}
          <div className="relative" ref={dropdownRef}>
            <label className="block text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Crop
            </label>
            <button
              type="button"
              onClick={() => setIsCropDropdownOpen(!isCropDropdownOpen)}
              className="btn-21st btn-21st-secondary w-full justify-between p-2.5 sm:p-3 rounded-lg cursor-pointer hover:border-slate-400 transition-all text-left"
            >
              <div className="flex items-center gap-2 min-w-0">
                <span className="font-semibold text-xs sm:text-sm truncate">
                  {currentCropObj.name}
                </span>
                <span className="text-[11px] opacity-70 font-normal truncate hidden xs:inline">
                  ({currentCropObj.category})
                </span>
              </div>
              <ChevronDown className="w-4 h-4 opacity-70 shrink-0 ml-1" />
            </button>

            {isCropDropdownOpen && (
              <div className="absolute z-30 mt-2 w-full farming-dropdown-menu rounded-lg shadow-lg overflow-hidden max-h-72 flex flex-col">
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
                    <span>{filteredCrops.length} crops</span>
                  </div>
                </div>
                <div className="overflow-y-auto p-1 divide-y divide-slate-100 dark:divide-slate-700/40 max-h-64">
                  {filteredCrops.map((c) => (
                    <button
                      key={c.name}
                      type="button"
                      onClick={() => handleCropSelect(c.name)}
                      className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-700/60 transition-colors rounded-xl cursor-pointer"
                    >
                      <div className="flex items-center gap-2.5 truncate">
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
                      No crop found.
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
                    className={`btn-21st btn-21st-pill btn-21st-xs font-bold transition-all cursor-pointer ${
                      isSelected ? "btn-21st-primary" : "btn-21st-secondary"
                    }`}
                  >
                    {c.name}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 2. Field Size & Unit */}
          <div>
            <label className="block text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Field size
            </label>
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 mb-2">
              {/* Numeric stepper */}
              <div className="flex-1 flex items-center justify-between bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg p-1">
                <button
                  type="button"
                  onClick={() => setFieldSize(Math.max(0.1, Number((fieldSize - 0.5).toFixed(1))))}
                  className="btn-21st btn-21st-secondary rounded-md w-8 h-8 sm:w-9 sm:h-9 p-0 flex items-center justify-center shrink-0 cursor-pointer"
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
                  className="w-full text-center font-semibold text-base sm:text-lg text-slate-900 dark:text-white bg-transparent focus:outline-none"
                />
                <button
                  type="button"
                  onClick={() => setFieldSize(Number((fieldSize + 0.5).toFixed(1)))}
                  className="btn-21st btn-21st-secondary rounded-md w-8 h-8 sm:w-9 sm:h-9 p-0 flex items-center justify-center shrink-0 cursor-pointer"
                  title="Increase field size"
                  aria-label="Increase field size"
                >
                  <Plus className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                </button>
              </div>

              {/* Units segmented toggle */}
              <div className="flex bg-slate-100 dark:bg-slate-800/90 p-1 rounded-lg border border-slate-200 dark:border-slate-700 justify-center gap-1">
                {(["Acre", "Hectare", "Gunta"] as const).map((unit) => {
                  const isSelected = fieldUnit === unit;
                  return (
                    <button
                      key={unit}
                      type="button"
                      onClick={() => setFieldUnit(unit)}
                      className={`btn-21st btn-21st-pill btn-21st-xs font-bold transition-all cursor-pointer ${
                        isSelected ? "btn-21st-primary" : "btn-21st-secondary"
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
            <label className="block text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Season
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
                    className={`btn-21st farming-season-btn p-2 sm:p-2.5 rounded-lg text-left flex flex-col justify-between transition-all cursor-pointer ${
                      isSel ? "btn-21st-primary" : "btn-21st-secondary"
                    }`}
                  >
                    <div className="w-full flex items-center justify-between mb-1">
                      <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4 opacity-80" />
                    </div>
                    <span className="text-[11px] sm:text-xs font-medium leading-tight truncate">{s.label}</span>
                  </button>
                );
              })}
            </div>
            {season === "Summer" && (
              <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 mt-1.5">
                Summer plan keeps some weed cover between rows to hold moisture.
              </p>
            )}
          </div>

          {/* 4. Soil Type & 5. Irrigation */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Soil
              </label>
              <select
                value={soilType}
                onChange={(e) => setSoilType(e.target.value)}
                className="w-full p-2.5 text-xs sm:text-sm font-semibold bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:border-blue-500"
              >
                {SOIL_TYPES.map((st) => (
                  <option key={st} value={st}>
                    {st}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                Irrigation
              </label>
              <select
                value={irrigationStatus}
                onChange={(e) => setIrrigationStatus(e.target.value)}
                className="w-full p-2.5 text-xs sm:text-sm font-semibold bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:border-blue-500"
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
              <label className="text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300">
                Weed cover
              </label>
              <span className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                More weeds means more fertilizer
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
                    className={`btn-21st farming-weed-pressure-btn p-2.5 sm:p-3 rounded-lg text-left transition-all relative overflow-hidden cursor-pointer ${
                      isSel ? "btn-21st-primary" : "btn-21st-secondary"
                    }`}
                  >
                    <div className="w-full">
                      <div className="text-[11px] sm:text-xs font-medium mb-0.5 truncate">{wp.label}</div>
                      <div className="text-[10px] sm:text-[11px] opacity-75 truncate">
                        {wp.buffer > 0 ? `+${wp.buffer}% fertilizer` : "No change"}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 7. Weed Types Present */}
          <div className="md:col-span-2">
            <label className="block text-xs sm:text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Weeds in the field
            </label>
            <div className="flex flex-wrap gap-1.5 sm:gap-2">
              {AVAILABLE_WEED_TYPES.map((wt) => {
                const isChecked = selectedWeeds.includes(wt.label);
                return (
                  <button
                    key={wt.id}
                    type="button"
                    onClick={() => toggleWeedType(wt.label)}
                    className={`btn-21st btn-21st-pill btn-21st-xs font-medium transition-all cursor-pointer select-none max-w-full min-w-0 ${
                      isChecked ? "btn-21st-primary" : "btn-21st-secondary"
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
                    <span className="truncate" title={wt.label}>{wt.label}</span>
                    {wt.isInvasive && <span className="opacity-70 font-normal shrink-0">· invasive</span>}
                  </button>
                );
              })}
            </div>
          </div>

          {/* ── Optional Customizable Parameters: Seed Spacing & Net Margin Economics ── */}
          {showAdvancedSettings && (
            <div className="md:col-span-2 p-3.5 sm:p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-2.5">Seed and spacing</h4>
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
                <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-2.5">Yield, price and cost</h4>
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
            Estimates only. Check your soil test card before buying fertilizer.
          </p>

          <button
            type="button"
            onClick={handleCalculate}
            className="btn-21st btn-21st-primary w-full sm:w-auto px-6 py-2.5 text-sm font-semibold cursor-pointer"
          >
            Calculate
          </button>
        </div>
      </div>

      {/* ── CALCULATED STRUCTURED OUTPUT SECTIONS ── */}
      {hasCalculated && (
        <div ref={resultsRef} className="space-y-4 sm:space-y-6 animate-in fade-in duration-300">
          {/* Header Summary Banner */}
          <div className="farming-card rounded-xl p-4 sm:p-5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h2 className="text-base sm:text-lg font-semibold text-slate-900 dark:text-white">
                  {currentCropObj.name} · {season}
                </h2>
                <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-xl">
                  Formulated for {fieldSize} {fieldUnit} ({acres.toFixed(2)} Acres / {hectares.toFixed(2)} Ha) on{" "}
                  {soilType} soil with {irrigationStatus} irrigation.
                </p>
              </div>

              <div className="grid grid-cols-2 sm:flex sm:items-center gap-2 sm:gap-3 w-full sm:w-auto">
                {weedLossPenaltyPct > 0 && (
                  <div className="rounded-lg p-2.5 sm:p-3 border border-slate-200 dark:border-slate-700 text-left sm:text-right">
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate">Yield lost to weeds</div>
                    <div className="text-base sm:text-lg font-semibold text-slate-900 dark:text-white">~{weedLossPenaltyPct}%</div>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400">+{bufferPercent}% fertilizer</div>
                  </div>
                )}
                <div className="rounded-lg p-2.5 sm:p-3 border border-slate-200 dark:border-slate-700 text-left sm:text-right">
                  <div className="text-[11px] text-slate-500 dark:text-slate-400 truncate">Profit</div>
                  <div className={`text-base sm:text-xl font-semibold truncate ${economics.netMargin >= 0 ? "text-emerald-700 dark:text-emerald-400" : "text-red-600 dark:text-red-400"}`}>
                    ₹{economics.netMargin.toLocaleString()}
                  </div>
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">{economics.roiPercent}% on cost</div>
                </div>
              </div>
            </div>
          </div>

          {/* ── Navigation Tab Switcher ── */}
          <div className="flex bg-slate-100 dark:bg-slate-800 p-1 sm:p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 overflow-x-auto no-scrollbar scroll-smooth gap-1 sm:gap-1.5">
            <button
              type="button"
              onClick={() => setActiveTab("all")}
              className={`btn-21st btn-21st-pill btn-21st-xs font-bold whitespace-nowrap transition-all cursor-pointer ${
                activeTab === "all" ? "btn-21st-primary" : "btn-21st-secondary"
              }`}
            >
              All
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("seed")}
              className={`btn-21st btn-21st-pill btn-21st-xs font-bold whitespace-nowrap transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                activeTab === "seed" ? "btn-21st-primary" : "btn-21st-secondary"
              }`}
            >
              Seed
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("economics")}
              className={`btn-21st btn-21st-pill btn-21st-xs font-bold whitespace-nowrap transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                activeTab === "economics" ? "btn-21st-primary" : "btn-21st-secondary"
              }`}
            >
              Yield & profit
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("nutrition")}
              className={`btn-21st btn-21st-pill btn-21st-xs font-bold whitespace-nowrap transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
                activeTab === "nutrition" ? "btn-21st-primary" : "btn-21st-secondary"
              }`}
            >
              Fertilizer & weeds
            </button>
          </div>

          {/* ════════ PILLAR A: SEED REQUIREMENT CALCULATOR ════════ */}
          {(activeTab === "all" || activeTab === "seed") && (
            <div className="farming-card rounded-xl p-4 sm:p-6 md:p-7">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2.5">
                  <div>
                    <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                      Seed
                    </h3>
                    <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                      Calculated using crop spacing ({rowSpacingInches}&Prime; &times; {plantSpacingInches}&Prime;), {germinationPercent}% germination, and {purityPercent}% seed purity.
                    </p>
                  </div>
                </div>
              </div>

              {/* Stat Cards for Seed Requirements */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-3.5 mb-4 sm:mb-5">
                <div className="farming-stat-card rounded-lg p-3.5 sm:p-4">
                  <div className="text-[11px] sm:text-xs font-bold farming-stat-label mb-1">
                    Seed to buy
                  </div>
                  <div className="text-2xl sm:text-3xl font-semibold farming-stat-value truncate">
                    {seedRequirement.totalWeightKg} <span className="text-xs sm:text-sm font-semibold opacity-75">kg</span>
                  </div>
                  <div className="text-[10px] sm:text-xs farming-stat-sub mt-1.5 font-medium">
                    Test Weight: {seedWeightGramsThousand}g per 1000 seeds
                  </div>
                </div>

                <div className="farming-stat-card rounded-lg p-3.5 sm:p-4">
                  <div className="text-[11px] sm:text-xs font-bold farming-stat-label mb-1">
                    Plants
                  </div>
                  <div className="text-2xl sm:text-3xl font-semibold farming-stat-value truncate">
                    {seedRequirement.totalPlants.toLocaleString()}
                  </div>
                  <div className="text-[10px] sm:text-xs farming-stat-sub mt-1.5 font-medium">
                    Target population for {acres.toFixed(2)} acres
                  </div>
                </div>

                <div className="farming-stat-card rounded-lg p-3.5 sm:p-4">
                  <div className="text-[11px] sm:text-xs font-bold farming-stat-label mb-1">
                    Seeds to sow
                  </div>
                  <div className="text-2xl sm:text-3xl font-semibold farming-stat-value truncate">
                    {seedRequirement.totalSeeds.toLocaleString()}
                  </div>
                  <div className="text-[10px] sm:text-xs farming-stat-sub mt-1.5 font-medium">
                    Includes {100 - germinationPercent}% buffer for emergence
                  </div>
                </div>
              </div>

              {/* Spacing Details Bar */}
              <div className="p-3 sm:p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs">
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
            <div className="farming-card rounded-xl p-4 sm:p-6 md:p-7">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                <div className="flex items-center gap-2.5">
                  <div>
                    <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                      Yield and profit
                    </h3>
                    <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                      Financial forecast based on {expectedYieldQtlAc} Qtl/ac harvest and ₹{sellingPriceQtl}/Qtl market price.
                    </p>
                  </div>
                </div>
                <div className="self-start sm:self-auto">
                  <span className="text-xs text-slate-500 dark:text-slate-400">{economics.roiPercent}% return on cost</span>
                </div>
              </div>

              {/* Economic KPI Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3.5 mb-4 sm:mb-5">
                <div className="farming-stat-card rounded-lg p-3 sm:p-4">
                  <div className="text-[10px] sm:text-xs font-bold farming-stat-label mb-1 truncate">
                    Harvest
                  </div>
                  <div className="text-lg xs:text-xl sm:text-2xl font-semibold farming-stat-value truncate">
                    {economics.totalProductionQtl} <span className="text-[11px] sm:text-xs font-semibold opacity-70">Qtl</span>
                  </div>
                  <div className="text-[10px] sm:text-[11px] farming-stat-sub mt-1 truncate">
                    ≈ {economics.totalProductionTonnes} Tonnes
                  </div>
                </div>

                <div className="farming-stat-card rounded-lg p-3 sm:p-4">
                  <div className="text-[10px] sm:text-xs font-bold farming-stat-label mb-1 truncate">
                    Income
                  </div>
                  <div className="text-lg xs:text-xl sm:text-2xl font-semibold farming-stat-value truncate" title={`₹${economics.grossRevenue.toLocaleString()}`}>
                    ₹{economics.grossRevenue.toLocaleString()}
                  </div>
                  <div className="text-[10px] sm:text-[11px] farming-stat-sub mt-1 truncate">
                    At ₹{sellingPriceQtl}/Qtl
                  </div>
                </div>

                <div className="farming-stat-card rounded-lg p-3 sm:p-4">
                  <div className="text-[10px] sm:text-xs font-bold farming-stat-label mb-1 truncate">
                    Cost
                  </div>
                  <div className="text-lg xs:text-xl sm:text-2xl font-semibold farming-stat-value truncate" title={`₹${economics.totalCost.toLocaleString()}`}>
                    ₹{economics.totalCost.toLocaleString()}
                  </div>
                  <div className="text-[10px] sm:text-[11px] farming-stat-sub mt-1 truncate">
                    ₹{costOfCultivationAc.toLocaleString()}/ac
                  </div>
                </div>

                <div className="farming-stat-card farming-stat-profit rounded-lg p-3 sm:p-4">
                  <div className="text-[10px] sm:text-xs font-semibold farming-stat-label-profit mb-1 truncate">
                    Profit
                  </div>
                  <div className="text-lg xs:text-xl sm:text-2xl font-semibold farming-stat-profit-val truncate" title={`₹${economics.netMargin.toLocaleString()}`}>
                    ₹{economics.netMargin.toLocaleString()}
                  </div>
                  <div className="text-[10px] sm:text-[11px] font-bold farming-stat-sub-profit mt-1 truncate">
                    ₹{economics.netMarginPerAcre.toLocaleString()}/ac
                  </div>
                </div>
              </div>

              {/* Benefit-Cost Ratio Bar */}
              <p className="text-xs text-slate-600 dark:text-slate-300">
                Every ₹1 spent brings back ₹{economics.benefitCostRatio}. Profit = income &minus; cost.
              </p>
            </div>
          )}

          {/* ════════ PILLAR C: PRECISION NUTRIENTS & WEED MANAGEMENT ════════ */}
          {(activeTab === "all" || activeTab === "nutrition") && (
            <div className="space-y-4 sm:space-y-6">
              {/* Section 1: Quantitative Input Adjustments */}
              <div className="farming-card rounded-xl p-4 sm:p-6 md:p-7">
                <div className="flex items-center gap-2.5 mb-4">
                  <div>
                    <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                      Fertilizer
                    </h3>
                    <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                      Amounts for your field size, including extra for weeds.
                    </p>
                  </div>
                </div>

                {/* Nutrients Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-3.5 mb-4 sm:mb-5">
                  {/* Nitrogen */}
                  <div className="farming-stat-card rounded-lg p-3.5 sm:p-4">
                    <div className="flex items-center justify-between text-xs font-bold farming-stat-label mb-1">
                      <span>Nitrogen (N)</span>
                      <span className="text-[11px] font-normal">+{bufferPercent}%</span>
                    </div>
                    <div className="text-xl sm:text-2xl font-semibold farming-stat-value">
                      {adjustedN.toFixed(1)} <span className="text-xs font-medium opacity-70">kg pure N</span>
                    </div>
                    <div className="text-xs farming-stat-sub mt-2 pt-2 border-t border-slate-200 dark:border-slate-700/80 flex items-center justify-between">
                      <span>Urea (46% N):</span>
                      <span className="font-semibold text-slate-900 dark:text-white">{ureaBags} bags (50kg)</span>
                    </div>
                  </div>

                  {/* Phosphorus */}
                  <div className="farming-stat-card rounded-lg p-3.5 sm:p-4">
                    <div className="flex items-center justify-between text-xs font-bold farming-stat-label mb-1">
                      <span>Phosphorus (P₂O₅)</span>
                      <span className="text-[11px] font-normal">+{bufferPercent}%</span>
                    </div>
                    <div className="text-xl sm:text-2xl font-semibold farming-stat-value">
                      {adjustedP.toFixed(1)} <span className="text-xs font-medium opacity-70">kg pure P₂O₅</span>
                    </div>
                    <div className="text-xs farming-stat-sub mt-2 pt-2 border-t border-slate-200 dark:border-slate-700/80 flex items-center justify-between">
                      <span>DAP (18-46-0):</span>
                      <span className="font-semibold text-slate-900 dark:text-white">{dapBags} bags (50kg)</span>
                    </div>
                  </div>

                  {/* Potassium */}
                  <div className="farming-stat-card rounded-lg p-3.5 sm:p-4">
                    <div className="flex items-center justify-between text-xs font-bold farming-stat-label mb-1">
                      <span>Potassium (K₂O)</span>
                      <span className="text-[11px] font-normal">+{bufferPercent}%</span>
                    </div>
                    <div className="text-xl sm:text-2xl font-semibold farming-stat-value">
                      {adjustedK.toFixed(1)} <span className="text-xs font-medium opacity-70">kg pure K₂O</span>
                    </div>
                    <div className="text-xs farming-stat-sub mt-2 pt-2 border-t border-slate-200 dark:border-slate-700/80 flex items-center justify-between">
                      <span>MOP (60% K₂O):</span>
                      <span className="font-semibold text-slate-900 dark:text-white">{mopBags} bags (50kg)</span>
                    </div>
                  </div>
                </div>

                {/* Application Method Callout */}
                <div className="border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 sm:p-4">
                  <div>
                    <div className="min-w-0">
                      <div className="text-xs text-slate-500 dark:text-slate-400">How to apply</div>
                      <div className="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white mt-0.5">
                        {applicationMethodTitle}
                      </div>
                      <p className="text-[11px] sm:text-xs text-slate-700 dark:text-slate-300 mt-1 leading-relaxed">
                        {applicationMethodDetail}
                      </p>

                      <div className="grid grid-cols-3 gap-1.5 sm:gap-2 mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 text-center">
                        <div className="farming-subcard rounded-md p-1.5 sm:p-2">
                          <div className="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 font-semibold truncate">At sowing</div>
                          <div className="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white">{basalSplitPct}%</div>
                        </div>
                        <div className="farming-subcard rounded-md p-1.5 sm:p-2">
                          <div className="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 font-semibold truncate">1st top-up</div>
                          <div className="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white">{topdress1SplitPct}%</div>
                          <div className="text-[9px] text-slate-400 hidden xs:block">after weeding</div>
                        </div>
                        <div className="farming-subcard rounded-md p-1.5 sm:p-2">
                          <div className="text-[10px] sm:text-[11px] text-slate-500 dark:text-slate-400 font-semibold truncate">2nd top-up</div>
                          <div className="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white">{topdress2SplitPct}%</div>
                          <div className="text-[9px] text-slate-400 hidden xs:block">at flowering</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Section 2: Season-Specific Weed & Microclimate Management */}
              <div className="farming-card rounded-xl p-4 sm:p-6 md:p-7">
                <div className="flex items-center gap-2.5 mb-4">
                  <div>
                    <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                      Weed control
                    </h3>
                    <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                      What to remove and what to leave this season.
                    </p>
                  </div>
                </div>

                {/* Summer Rule B Highlight */}
                {isSummerSeason ? (
                  <div className="border border-slate-200 dark:border-slate-700 rounded-lg p-4 mb-4 sm:mb-5">
                    <div>
                      <div>
                        <div className="text-sm font-semibold text-slate-900 dark:text-white">
                          In summer, don&apos;t clear every weed
                        </div>
                        <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
                          Bare soil heats up, dries out and forms a crust. That hurts the crop more than a few
                          weeds between rows.
                        </p>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3 mt-3 sm:mt-4">
                          {/* Root Zone */}
                          <div className="farming-subcard rounded-lg p-3 sm:p-3.5">
                            <div className="text-xs font-semibold text-slate-900 dark:text-white mb-1">Near the plant (0–15 cm)</div>
                            <p className="text-[11px] sm:text-xs text-slate-700 dark:text-slate-300 font-medium leading-relaxed">
                              Keep 100% clean through localized ring weeding. Eliminates direct competition for water, space,
                              and applied fertilizers.
                            </p>
                          </div>

                          {/* Inter-Row Space */}
                          <div className="farming-subcard rounded-lg p-3 sm:p-3.5">
                            <div className="text-xs font-semibold text-slate-900 dark:text-white mb-1">Between rows (&gt;15 cm)</div>
                            <p className="text-[11px] sm:text-xs text-slate-700 dark:text-slate-300 font-medium leading-relaxed">
                              Do NOT uproot non-aggressive weeds! Instead, <strong>slash / mow at ground level</strong> and
                              leave biomass on the surface as <strong>green surface mulch</strong>.
                            </p>
                          </div>
                        </div>

                        {/* Quantified Benefits */}
                        <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
                          Mulch lowers soil temperature by 4–8°C, cuts evaporation by up to 35% and adds organic matter.
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="border border-slate-200 dark:border-slate-700 rounded-lg p-3.5 sm:p-4 mb-4 sm:mb-5">
                    <div className="text-sm font-semibold text-slate-900 dark:text-white mb-1">{season}</div>
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
                  <div className="rounded-lg p-3.5 sm:p-4 border border-slate-200 dark:border-slate-700 border-l-4 border-l-emerald-600">
                    <div className="text-sm font-semibold text-slate-900 dark:text-white mb-2">Cut and leave as mulch</div>
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
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                      Slash with sickle/mower and spread evenly as a 3–5 cm blanket between crop rows.
                    </div>
                  </div>

                  {/* Noxious / Invasive to Remove Immediately */}
                  <div className="rounded-lg p-3.5 sm:p-4 border border-slate-200 dark:border-slate-700 border-l-4 border-l-red-600">
                    <div className="text-sm font-semibold text-slate-900 dark:text-white mb-2">Pull out now</div>
                    {invasiveWeeds.length > 0 ? (
                      <ul className="text-[11px] sm:text-xs text-slate-700 dark:text-slate-300 space-y-1.5 list-disc list-inside">
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
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-2">
                      Never use Parthenium or Motha as mulch: they harm the soil and spread underground. Pull them out
                      before they flower.
                    </div>
                  </div>
                </div>
              </div>

              {/* Section 3: High-Yield Action Plan */}
              <div className="farming-card rounded-xl p-4 sm:p-6 md:p-7">
                <div className="flex items-center gap-2.5 mb-4 sm:mb-5">
                  <div>
                    <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                      What to do and when
                    </h3>
                    <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400">
                      From sowing to full growth.
                    </p>
                  </div>
                </div>

                <div className="space-y-3 sm:space-y-4">
                  {/* Step 1 */}
                  <div className="farming-step-card flex items-start gap-2.5 sm:gap-3.5 p-3 sm:p-3.5 rounded-lg">
                    <div className="w-6 text-sm font-semibold text-slate-400 shrink-0 tabular-nums">1.</div>
                    <div>
                      <div className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
                        Day 0–15: weed around plants, apply first dose
                      </div>
                      <p className="text-[11px] sm:text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
                        Perform localized ring weeding in the 0–15 cm strip around each seedling. Apply basal fertilizer (
                        {basalSplitPct}% of total) banded 5–10 cm to the side of the seed line. In summer, retain inter-row
                        slashed green mulch immediately to insulate moist soil.
                      </p>
                    </div>
                  </div>

                  {/* Step 2 */}
                  <div className="farming-step-card flex items-start gap-2.5 sm:gap-3.5 p-3 sm:p-3.5 rounded-lg">
                    <div className="w-6 text-sm font-semibold text-slate-400 shrink-0 tabular-nums">2.</div>
                    <div>
                      <div className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
                        Weed first, then add nitrogen
                      </div>
                      <p className="text-[11px] sm:text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
                        Nitrogen put into weedy rows feeds the weeds. Clear or cut weeds first, then apply the top-up
                        dose <strong>1–2 days later</strong>.
                      </p>
                    </div>
                  </div>

                  {/* Step 3 */}
                  <div className="farming-step-card flex items-start gap-2.5 sm:gap-3.5 p-3 sm:p-3.5 rounded-lg">
                    <div className="w-6 text-sm font-semibold text-slate-400 shrink-0 tabular-nums">3.</div>
                    <div>
                      <div className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">
                        Watering ({irrigationStatus.toLowerCase()})
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
                <div className="mt-4 sm:mt-5 p-3 sm:p-4 rounded-lg border border-amber-300 dark:border-amber-700/60 flex items-start gap-2.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="text-sm font-semibold text-slate-900 dark:text-white">Check your soil test first</div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 mt-0.5 leading-relaxed">
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
