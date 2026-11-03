export interface FormulationDiseaseTarget {
  name: string;
  dosage: number;
  dosageUnit: string;
  waterAmount: number;
  waterUnit: string;
}

export interface FormulationCropUse {
  cropName: string;
  cropEmoji: string;
  diseases: FormulationDiseaseTarget[];
}

export type PesticideCategory =
  | "Insecticide"
  | "Fungicide"
  | "Bactericide"
  | "Virucide"
  | "Herbicide"
  | "Acaricide"
  | "Nematicide"
  | "Bio-pesticide";

export interface PesticideFormulation {
  id: string;
  name: string;
  category: PesticideCategory;
  popularBrand: string;
  description: string;
  crops: FormulationCropUse[];
}

export const PESTICIDES_DATABASE: PesticideFormulation[] = [
  // ─── INSECTICIDES ───
  {
    id: "chlorpyrifos-50-ec",
    name: "Chlorpyrifos 50.0% EC",
    category: "Insecticide",
    popularBrand: "Radar / Dursban / Classic",
    description: "Broad-spectrum organophosphate contact and stomach insecticide for soil and foliar pests.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Yellow Stem Borer", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Rice Leafroller", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Gall Midge", dosage: 450, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Rice Hispa", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Helicoverpa Caterpillar", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Pink Bollworm", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Spiny Bollworm", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Spotted Bollworm", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Cutworm", dosage: 450, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Cutworm & Tuber Moth", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Aphids", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "Early Shoot Borer", dosage: 800, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
          { name: "Termites & Root Borer", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Thrips & Maggots", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "chlorantraniliprole-18-5-sc",
    name: "Chlorantraniliprole 18.5% SC",
    category: "Insecticide",
    popularBrand: "Coragen / Vesticor",
    description: "Novel anthranilic diamide targeting ryanodine receptors with ultra-long caterpillar protection.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer (Helicoverpa)", dosage: 60, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Pinworm (Tuta absoluta)", dosage: 60, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Yellow Stem Borer", dosage: 60, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Leaf Folder", dosage: 60, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Fruit Borer & Spodoptera", dosage: 60, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "American Bollworm & Spotted Bollworm", dosage: 60, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Maize",
        cropEmoji: "🌽",
        diseases: [
          { name: "Fall Armyworm (Spodoptera frugiperda)", dosage: 80, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Stem Borer", dosage: 60, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "Early Shoot Borer & Top Borer", dosage: 150, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Green Semilooper & Spodoptera", dosage: 60, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "imidacloprid-17-8-sl",
    name: "Imidacloprid 17.8% SL",
    category: "Insecticide",
    popularBrand: "Confidor / Victor / Tathastu",
    description: "Systemic neonicotinoid insecticide delivering exceptional control against sucking insect pests.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whiteflies & Jassids", dosage: 40, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Aphids & Thrips", dosage: 40, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown Plant Hopper (BPH)", dosage: 50, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Green Leafhopper", dosage: 50, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Chilli Thrips & Aphids", dosage: 50, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Whiteflies & Leaf Curl Vectors", dosage: 50, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Aphids & Jassids", dosage: 50, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Mango",
        cropEmoji: "🥭",
        diseases: [
          { name: "Mango Hopper", dosage: 80, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "Termites & Woolly Aphid", dosage: 150, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "emamectin-benzoate-5-sg",
    name: "Emamectin Benzoate 5% SG",
    category: "Insecticide",
    popularBrand: "Proclaim / Missile / Kingclaim",
    description: "Naturally derived avermectin insecticide with strong translaminar caterpillar knockdown.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Helicoverpa & Bollworm Complex", dosage: 88, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Spodoptera Caterpillar", dosage: 88, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer", dosage: 80, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Pinworm (Tuta absoluta)", dosage: 80, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Fruit Borer & Thrips", dosage: 80, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Maize",
        cropEmoji: "🌽",
        diseases: [
          { name: "Fall Armyworm (FAW)", dosage: 100, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Diamondback Moth (DBM)", dosage: 80, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Gram / Chickpea",
        cropEmoji: "🫘",
        diseases: [
          { name: "Pod Borer (Helicoverpa armigera)", dosage: 88, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Thrips & Berry Borer", dosage: 100, dosageUnit: "g/ac", waterAmount: 250, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "spinetoram-11-7-sc",
    name: "Spinetoram 11.7% SC",
    category: "Insecticide",
    popularBrand: "Delegate / Summit / Spintor",
    description: "Spinosyn family insecticide fermentation product with fast contact & ingestion control of resistant pests.",
    crops: [
      {
        cropName: "Maize",
        cropEmoji: "🌽",
        diseases: [
          { name: "Fall Armyworm (FAW)", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Black Thrips (Thrips parvispinus)", dosage: 160, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Fruit Borer", dosage: 160, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Thrips & Tobacco Caterpillar", dosage: 170, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Spodoptera & Semilooper", dosage: 180, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Onion Thrips", dosage: 160, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "fipronil-5-sc",
    name: "Fipronil 5.0% SC",
    category: "Insecticide",
    popularBrand: "Regent / Mahaveer / Mortar",
    description: "Broad-spectrum phenylpyrazole insecticide with xylem systemic action and plant growth boost.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Yellow Stem Borer", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Brown Plant Hopper (BPH)", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Gall Midge & Leaf Folder", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Chilli Thrips & Yellow Mites", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Fruit Borer", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Aphids, Jassids & Thrips", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Whitefly", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "Early Shoot Borer & Root Borer", dosage: 600, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Thrips & Maggots", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "cartap-hydrochloride-50-sp",
    name: "Cartap Hydrochloride 50% SP",
    category: "Insecticide",
    popularBrand: "Caldan / Padan / Kritap",
    description: "Nereistoxin analogue insecticide with rapid feeding cessation of lepidopteran borers.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Yellow Stem Borer", dosage: 400, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Leaf Folder", dosage: 400, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Whorl Maggot", dosage: 400, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Diamondback Moth (DBM)", dosage: 400, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer & Leafminer", dosage: 400, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "pymetrozine-50-wg",
    name: "Pymetrozine 50% WG",
    category: "Insecticide",
    popularBrand: "Chess / Plenum",
    description: "Specialized sucking pest inhibitor causing irreversible stylet block in planthoppers within hours.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown Plant Hopper (BPH)", dosage: 120, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "White Backed Plant Hopper (WBPH)", dosage: 120, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "diafenthiuron-50-wp",
    name: "Diafenthiuron 50% WP",
    category: "Insecticide",
    popularBrand: "Pegasus / Polo / Agas",
    description: "Unique thiourea-derived insecticide-acaricide converted into carbodiimide by sunlight.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly (Adults & Nymphs)", dosage: 240, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Aphids, Jassids & Red Spider Mites", dosage: 240, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Yellow Mites & Whitefly", dosage: 240, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Thrips", dosage: 240, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Whitefly & Red Spider Mites", dosage: 240, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Diamondback Moth (DBM)", dosage: 240, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "flubendiamide-39-35-sc",
    name: "Flubendiamide 39.35% SC",
    category: "Insecticide",
    popularBrand: "Fame / Fluben",
    description: "Powerful ryanodine receptor modulator providing stellar caterpillar and borer control.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Yellow Stem Borer", dosage: 24, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Leaf Folder", dosage: 24, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "American Bollworm & Spotted Bollworm", dosage: 40, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer (Helicoverpa)", dosage: 40, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Fruit Borer", dosage: 40, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Pigeonpea / Pulses",
        cropEmoji: "🫘",
        diseases: [
          { name: "Pod Borer & Plume Moth", dosage: 40, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "thiamethoxam-25-wg",
    name: "Thiamethoxam 25% WG",
    category: "Insecticide",
    popularBrand: "Actara / Extra / Anant",
    description: "Second-generation neonicotinoid with systemic translaminar action and crop vigor enhancement.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Green Leafhopper & BPH", dosage: 40, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Stem Borer & Gall Midge", dosage: 40, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Jassids, Aphids & Whitefly", dosage: 40, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Whitefly & Aphids", dosage: 50, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Aphids", dosage: 40, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Wheat",
        cropEmoji: "🌾",
        diseases: [
          { name: "Aphids", dosage: 30, dosageUnit: "g/ac", waterAmount: 150, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Mango",
        cropEmoji: "🥭",
        diseases: [
          { name: "Mango Hopper", dosage: 60, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "acetamiprid-20-sp",
    name: "Acetamiprid 20% SP",
    category: "Insecticide",
    popularBrand: "Pride / Manik / Rekord",
    description: "Rapid penetrating systemic neonicotinoid targeting nicotinic acetylcholine receptors.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly, Aphids & Jassids", dosage: 40, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips & Aphids", dosage: 40, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Aphids", dosage: 30, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "profenofos-cypermethrin",
    name: "Profenofos 40% + Cypermethrin 4% EC",
    category: "Insecticide",
    popularBrand: "Roket / Polytrin C / Profex Super",
    description: "Synergistic combi-product offering explosive knockdown and ovicidal control of caterpillars and sucking pests.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bollworm Complex & Spodoptera", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Whitefly & Jassids", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Semilooper & Tobacco Caterpillar", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Fruit Borer & Mites", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "lambda-cyhalothrin-5-ec",
    name: "Lambda-cyhalothrin 5% EC",
    category: "Insecticide",
    popularBrand: "Karate / Silnet / Matador",
    description: "High-potency pyrethroid with rapid contact repellent and antifeedant properties.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bollworms, Jassids & Thrips", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Leaf Folder & Stem Borer", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Gall Midge & Hispa", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips & Pod Borer", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "neem-oil-10000-ppm",
    name: "Neem Oil 10,000 PPM (Azadirachtin 1%)",
    category: "Bio-pesticide",
    popularBrand: "Neemazal / Nimbecidine / EcoNeem",
    description: "Pure botanical biopesticide deterring feeding, oviposition and moulting without harming beneficials.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Whitefly, Leafminer & Early Borers", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly, Aphids & Early Bollworms", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Chilli Thrips & Mites", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown Plant Hopper & Leafhopper", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Vegetables (General)",
        cropEmoji: "🥦",
        diseases: [
          { name: "Sucking Pests & Caterpillar Eggs", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },

  // ─── FUNGICIDES ───
  {
    id: "mancozeb-75-wp",
    name: "Mancozeb 75% WP",
    category: "Fungicide",
    popularBrand: "Dithane M-45 / Indofil M-45 / Uthane",
    description: "Gold standard multi-site protective dithiocarbamate fungicide inhibiting fungal spore germination.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Early Blight & Late Blight", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Septoria Leaf Spot & Fruit Rot", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Early Blight & Late Blight", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Blast & Brown Spot", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Wheat",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown & Black Rust, Leaf Blight", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Anthracnose, Die-back & Fruit Rot", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Purple Blotch & Stemphylium Blight", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Tikka Leaf Spot", dosage: 500, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Downy Mildew & Anthracnose", dosage: 800, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "hexaconazole-5-sc",
    name: "Hexaconazole 5% SC",
    category: "Fungicide",
    popularBrand: "Contaf Plus / Sitara / Force",
    description: "Broad-spectrum systemic triazole fungicide with protective, curative, and eradicative properties.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Leaf Blast", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Grey Mildew & Leaf Spot", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Powdery Mildew & Die-back", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Mango",
        cropEmoji: "🥭",
        diseases: [
          { name: "Powdery Mildew", dosage: 400, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Rust", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Apple",
        cropEmoji: "🍎",
        diseases: [
          { name: "Scab & Powdery Mildew", dosage: 400, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "tricyclazole-75-wp",
    name: "Tricyclazole 75% WP",
    category: "Fungicide",
    popularBrand: "Baan / Beam / Sivic",
    description: "Specialized systemic blast inhibitor preventing melanin biosynthesis and appressorium penetration in rice.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Leaf Blast", dosage: 120, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Neck Blast & Node Blast", dosage: 120, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "azoxystrobin-difenoconazole",
    name: "Azoxystrobin 18.2% + Difenoconazole 11.4% SC",
    category: "Fungicide",
    popularBrand: "Amistar Top / Mirador Duo",
    description: "Dual-action strobilurin and triazole fungicide delivering unrivaled preventative and curative disease suppression.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Early Blight & Late Blight", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Anthracnose", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight & Blast", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Anthracnose, Die-back & Powdery Mildew", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Purple Blotch & Stemphylium Blight", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Maize",
        cropEmoji: "🌽",
        diseases: [
          { name: "Turcicum Leaf Blight & Maydis Blight", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "metalaxyl-mancozeb",
    name: "Metalaxyl 8% + Mancozeb 64% WP",
    category: "Fungicide",
    popularBrand: "Ridomil Gold / Krilaxyl / Matco",
    description: "Systemic acylalanine and contact dithiocarbamate fungicide specifically engineered for devastating Oomycetes.",
    crops: [
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Late Blight (Phytophthora infestans)", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Late Blight & Buckeye Rot", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Downy Mildew (Plasmopara viticola)", dosage: 800, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Mustard",
        cropEmoji: "🌾",
        diseases: [
          { name: "White Rust & Downy Mildew", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Black Pepper",
        cropEmoji: "🌿",
        diseases: [
          { name: "Quick Wilt (Phytophthora Foot Rot)", dosage: 800, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "carbendazim-mancozeb",
    name: "Carbendazim 12% + Mancozeb 63% WP",
    category: "Fungicide",
    popularBrand: "Saaf / Sprint / Companion",
    description: "Renowned combination fungicide controlling both seed-borne, soil-borne, and foliar fungal pathogens.",
    crops: [
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Tikka Leaf Spot & Collar Rot", dosage: 400, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Blast & Sheath Blight", dosage: 300, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Fruit Rot & Powdery Mildew", dosage: 300, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Early Blight & Black Scurf", dosage: 500, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tea",
        cropEmoji: "🍃",
        diseases: [
          { name: "Black Rot & Blister Blight", dosage: 500, dosageUnit: "g/ac", waterAmount: 250, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "copper-oxychloride-50-wp",
    name: "Copper Oxychloride 50% WP",
    category: "Fungicide",
    popularBrand: "Blitox / Fytolan / Blue Copper",
    description: "Inorganic protective copper fungicide and bactericide preventing spore germination through copper ion release.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Early Blight & Fruit Rot", dosage: 800, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Bacterial Canker & Spot", dosage: 800, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Early Blight & Late Blight", dosage: 800, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Citrus",
        cropEmoji: "🍊",
        diseases: [
          { name: "Citrus Canker & Gummosis", dosage: 1000, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Banana",
        cropEmoji: "🍌",
        diseases: [
          { name: "Sigatoka Leaf Spot & Tip Rot", dosage: 800, dosageUnit: "g/ac", waterAmount: 250, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "False Smut & Bacterial Leaf Blight", dosage: 800, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Anthracnose & Leaf Spot", dosage: 800, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "propiconazole-25-ec",
    name: "Propiconazole 25% EC",
    category: "Fungicide",
    popularBrand: "Tilt / Radar / Bumper",
    description: "Systemic triazole fungicide with powerful sterol biosynthesis inhibition for rusts and bunts.",
    crops: [
      {
        cropName: "Wheat",
        cropEmoji: "🌾",
        diseases: [
          { name: "Yellow Rust (Stripe Rust) & Brown Rust", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Karnal Bunt", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Tikka Leaf Spot", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Rust", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "tebuconazole-25-9-ec",
    name: "Tebuconazole 25.9% EC",
    category: "Fungicide",
    popularBrand: "Folicur / Raxil",
    description: "Systemic triazole with xylem translocation controlling foliar and fruit fungal pathogens.",
    crops: [
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Purple Blotch", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Fruit Rot & Powdery Mildew", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Rust", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight & False Smut", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "sulphur-80-wdg",
    name: "Sulphur 80% WDG",
    category: "Fungicide",
    popularBrand: "Sulfex / Insulf / Cosavet",
    description: "Micronized water-dispersible sulphur for eco-friendly powdery mildew and mite suppression.",
    crops: [
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Powdery Mildew", dosage: 800, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Mango",
        cropEmoji: "🥭",
        diseases: [
          { name: "Powdery Mildew", dosage: 1000, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Powdery Mildew & Mites", dosage: 800, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Pea / Pulses",
        cropEmoji: "🫛",
        diseases: [
          { name: "Powdery Mildew & Rust", dosage: 800, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },

  // ─── BACTERICIDES & VIRUCIDES ───
  {
    id: "streptocycline",
    name: "Streptocycline (Streptomycin 90% + Tetracycline 10%)",
    category: "Bactericide",
    popularBrand: "Streptocycline / Plantomycin",
    description: "Agricultural antibiotic bactericide inhibiting protein synthesis in phytopathogenic bacteria.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Bacterial Leaf Blight (BLB)", dosage: 15, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Bacterial Leaf Streak", dosage: 15, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Bacterial Wilt (Ralstonia solanacearum)", dosage: 20, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Bacterial Canker & Spot", dosage: 20, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Citrus",
        cropEmoji: "🍊",
        diseases: [
          { name: "Citrus Canker (Xanthomonas axonopodis)", dosage: 25, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bacterial Blight (Black Arm)", dosage: 20, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Pomegranate",
        cropEmoji: "🍎",
        diseases: [
          { name: "Bacterial Blight (Telya / Oily Spot)", dosage: 30, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Bacterial Leaf Spot", dosage: 20, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "kasugamycin-3-sl",
    name: "Kasugamycin 3% SL",
    category: "Bactericide",
    popularBrand: "Kasu-B / Bio-Kasu",
    description: "Aminoglycoside antibiotic controlling bacterial leaf blight and fungal blast simultaneously.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Blast & Bacterial Leaf Blight", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Bacterial Canker & Early Blight", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "copper-hydroxide-77-wp",
    name: "Copper Hydroxide 77% WP",
    category: "Bactericide",
    popularBrand: "Kocide 2000 / Paras",
    description: "Finely milled fixed copper protective bactericide and fungicide with superior tenacity against rains.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Bacterial Spot & Early Blight", dosage: 500, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Citrus",
        cropEmoji: "🍊",
        diseases: [
          { name: "Citrus Canker", dosage: 800, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Bacterial Spot & Anthracnose", dosage: 500, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Early & Late Blight", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "botanical-viricide-spray",
    name: "Botanical Viricide & Immunity Booster",
    category: "Virucide",
    popularBrand: "V-Bind / Viral Out / No-Virus",
    description: "Specialized botanical antiviral formulation inducing systemic acquired resistance against plant viruses.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Chilli Leaf Curl Virus (Gemini Virus)", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Yellow Mosaic Virus", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Tomato Leaf Curl Virus (ToLCV)", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Tomato Mosaic Virus (ToMV)", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Okra / Bhendi",
        cropEmoji: "🌱",
        diseases: [
          { name: "Yellow Vein Mosaic Virus (YVMV)", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Papaya",
        cropEmoji: "🍈",
        diseases: [
          { name: "Papaya Ring Spot Virus (PRSV)", dosage: 500, dosageUnit: "ml/ac", waterAmount: 250, waterUnit: "l/ac" },
        ],
      },
    ],
  },

  // ─── ACARICIDES (MITES) ───
  {
    id: "spiromesifen-22-9-sc",
    name: "Spiromesifen 22.9% SC",
    category: "Acaricide",
    popularBrand: "Oberon / Voltage",
    description: "Lipid biosynthesis inhibitor with ovicidal, nymphal, and adult fertility reduction in mites and whiteflies.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Yellow Mites & Whitefly", dosage: 160, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Red Spider Mites & Whitefly", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly & Red Spider Mites", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Brinjal",
        cropEmoji: "🍆",
        diseases: [
          { name: "Red Spider Mites", dosage: 160, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "propargite-57-ec",
    name: "Propargite 57% EC",
    category: "Acaricide",
    popularBrand: "Omite / Simbaa",
    description: "Sulfite ester acaricide providing exceptional residual knockdown against all motile mite stages.",
    crops: [
      {
        cropName: "Tea",
        cropEmoji: "🍃",
        diseases: [
          { name: "Red Spider Mites & Pink Mites", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Yellow Mites", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Apple",
        cropEmoji: "🍎",
        diseases: [
          { name: "European Red Mites", dosage: 500, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },

  // ─── HERBICIDES (WEEDICIDES) ───
  {
    id: "bispyribac-sodium-10-sc",
    name: "Bispyribac Sodium 10% SC",
    category: "Herbicide",
    popularBrand: "Nominee Gold / Adora / Tarang",
    description: "Post-emergence selective herbicide controlling grasses, sedges and broadleaf weeds in paddy.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Barnyard Grass (Echinochloa) & Sedges", dosage: 100, dosageUnit: "ml/ac", waterAmount: 150, waterUnit: "l/ac" },
          { name: "Broadleaf Weeds in Rice", dosage: 100, dosageUnit: "ml/ac", waterAmount: 150, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "pretilachlor-50-ec",
    name: "Pretilachlor 50% EC",
    category: "Herbicide",
    popularBrand: "Rifit / Eraze / Deliver",
    description: "Pre-emergence herbicide applied within 0-4 days after transplanting paddy to prevent weed germination.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Grasses, Sedges & Broadleaf Weeds", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "pendimethalin-30-ec",
    name: "Pendimethalin 30% EC",
    category: "Herbicide",
    popularBrand: "Stomp / Dhanutop / Panida",
    description: "Dinitroaniline pre-emergence selective herbicide creating a chemical barrier against weed emergence.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Annual Grasses & Broadleaf Weeds", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Annual Weeds & Grasses", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Broadleaf Weeds & Sedges", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Wheat",
        cropEmoji: "🌾",
        diseases: [
          { name: "Phalaris minor & Chenopodium", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Annual Grasses & Weeds", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "glyphosate-41-sl",
    name: "Glyphosate 41% SL",
    category: "Herbicide",
    popularBrand: "Roundup / Glycel / Sweep",
    description: "Non-selective broad-spectrum systemic herbicide translocating to roots of standing perennial weeds.",
    crops: [
      {
        cropName: "Tea",
        cropEmoji: "🍃",
        diseases: [
          { name: "Perennial Grasses, Sedges & Broadleaf Weeds", dosage: 800, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Non-Crop Land / Bunds",
        cropEmoji: "🌾",
        diseases: [
          { name: "Cyperus, Cynodon & Parthenium (Congress Grass)", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "2-4-d-amine-salt-58-sl",
    name: "2,4-D Amine Salt 58% SL",
    category: "Herbicide",
    popularBrand: "Weedmar / Main / Zura",
    description: "Selective post-emergence synthetic auxin herbicide eradicating broadleaf weeds without affecting monocots.",
    crops: [
      {
        cropName: "Wheat",
        cropEmoji: "🌾",
        diseases: [
          { name: "Broadleaf Weeds (Bathua, Melilotus)", dosage: 400, dosageUnit: "ml/ac", waterAmount: 150, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "Broadleaf Weeds & Cyperus", dosage: 800, dosageUnit: "ml/ac", waterAmount: 250, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Maize",
        cropEmoji: "🌽",
        diseases: [
          { name: "Broadleaf Weeds", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },

  // ─── NEMATICIDES ───
  {
    id: "fluopyram-34-48-sc",
    name: "Fluopyram 34.48% SC",
    category: "Nematicide",
    popularBrand: "Velum Prime",
    description: "Targeted mitochondrial complex II inhibitor paralyzing plant-parasitic nematodes within minutes.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Root-Knot Nematodes (Meloidogyne spp.)", dosage: 250, dosageUnit: "ml/ac", waterAmount: 250, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Root-Knot & Cyst Nematodes", dosage: 250, dosageUnit: "ml/ac", waterAmount: 250, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Pomegranate",
        cropEmoji: "🍎",
        diseases: [
          { name: "Root-Knot Nematodes (Drenching)", dosage: 300, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "carbofuran-3-cg",
    name: "Carbofuran 3% CG",
    category: "Nematicide",
    popularBrand: "Furadan / Diafuran",
    description: "Broad-spectrum systemic carbamate nematicide and soil insecticide protecting seedling root systems.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Root-Knot Nematodes", dosage: 10000, dosageUnit: "g/ac", waterAmount: 0, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Rice Root Nematode & Stem Borer", dosage: 10000, dosageUnit: "g/ac", waterAmount: 0, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Banana",
        cropEmoji: "🍌",
        diseases: [
          { name: "Burrowing Nematode & Corm Weevil", dosage: 12000, dosageUnit: "g/ac", waterAmount: 0, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "acephate-75-sp",
    name: "Acephate 75% SP",
    category: "Insecticide",
    popularBrand: "Asataf / Starthene / Tremor",
    description: "Systemic organophosphate insecticide highly effective against sucking pests, aphids, jassids, and leaf folders.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Aphids & Jassids", dosage: 350, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Bollworms & Whitefly", dosage: 400, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Green Leafhopper & Stem Borer", dosage: 300, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Rice Leaf folder", dosage: 350, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips & Aphids", dosage: 300, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Girdle Beetle & Stem Fly", dosage: 350, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "clothianidin-50-wdg",
    name: "Clothianidin 50% WDG",
    category: "Insecticide",
    popularBrand: "Dantop / Danto-Super",
    description: "Advanced neonicotinoid systemic insecticide with rapid translaminar and acropetal translocation against stubborn sucking pests.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown Plant Hopper (BPH)", dosage: 12, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "White Backed Plant Hopper", dosage: 12, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Jassids & Aphids", dosage: 15, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "Pyrilla & Termites", dosage: 50, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tea",
        cropEmoji: "🍵",
        diseases: [
          { name: "Mosquito Bug & Green Fly", dosage: 25, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "dinotefuran-20-sg",
    name: "Dinotefuran 20% SG",
    category: "Insecticide",
    popularBrand: "Token / Oshin / Osheen",
    description: "Third-generation neonicotinoid insecticide delivering exceptional knockdown of plant hoppers and sap-feeding pests.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown Plant Hopper (BPH)", dosage: 80, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "White Backed Plant Hopper", dosage: 80, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Jassids, Aphids & Whitefly", dosage: 60, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips & Whiteflies", dosage: 80, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "cyantraniliprole-10-26-od",
    name: "Cyantraniliprole 10.26% OD",
    category: "Insecticide",
    popularBrand: "Benevia / DuPont Cyazypyr",
    description: "Anthranilic diamide cross-spectrum insecticide giving long-lasting control of chewing borers and sucking pests.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Whitefly & Leaf Miner", dosage: 360, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Fruit Borer", dosage: 360, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips, Aphids & Fruit Borer", dosage: 360, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Thrips & Flea Beetle", dosage: 400, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "cypermethrin-10-ec",
    name: "Cypermethrin 10% EC",
    category: "Insecticide",
    popularBrand: "Ripcord / Bilcyp / Cyperhit",
    description: "High-activity synthetic pyrethroid contact insecticide targeting chewing caterpillars and fruit borers.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Spotted & Spiny Bollworm", dosage: 220, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Pink Bollworm", dosage: 280, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer (Helicoverpa)", dosage: 220, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Diamondback Moth", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "cypermethrin-25-ec",
    name: "Cypermethrin 25% EC",
    category: "Insecticide",
    popularBrand: "Ustaad / Cymbush / Colt",
    description: "Concentrated pyrethroid formulation providing rapid knockdown of lepidopteran larvae and beetles.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "American Bollworm & Pink Bollworm", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Fruit Borer", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Wheat",
        cropEmoji: "🌾",
        diseases: [
          { name: "Shoot Fly & Armyworm", dosage: 120, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "deltamethrin-2-8-ec",
    name: "Deltamethrin 2.8% EC",
    category: "Insecticide",
    popularBrand: "Decis / Delthrin",
    description: "Pure stereoisomer pyrethroid offering fast paralysis and high potency at low application doses.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bollworms & Leaf Roller", dosage: 180, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer & Caterpillars", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tea",
        cropEmoji: "🍵",
        diseases: [
          { name: "Tea Mosquito Bug & Thrips", dosage: 120, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "dimethoate-30-ec",
    name: "Dimethoate 30% EC",
    category: "Insecticide",
    popularBrand: "Rogor / Tafgor / Novagor",
    description: "Classic organophosphate systemic and contact insecticide effective against aphids, shoot flies, and mites.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips, Mites & Aphids", dosage: 260, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Jassids & Aphids", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Thrips & Maggots", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Mustard",
        cropEmoji: "🌼",
        diseases: [
          { name: "Mustard Aphid", dosage: 260, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "indoxacarb-14-5-sc",
    name: "Indoxacarb 14.5% SC",
    category: "Insecticide",
    popularBrand: "Avaunt / Kingdoxa",
    description: "Oxadiazine voltage-dependent sodium channel blocker for safe caterpillar and pod borer control.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer (Helicoverpa)", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "American Bollworm", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Fruit Borer & Cutworm", dosage: 160, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Diamondback Moth", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "novaluron-10-ec",
    name: "Novaluron 10% EC",
    category: "Insecticide",
    popularBrand: "Rimon / Novastar",
    description: "Chitin synthesis inhibitor insect growth regulator (IGR) disrupting larval moulting and foliage destruction.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Tomato Fruit Borer", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Spodoptera litura & Bollworm", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Diamondback Moth (DBM)", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "spirotetramat-15-31-od",
    name: "Spirotetramat 15.31% OD",
    category: "Insecticide",
    popularBrand: "Movento OD",
    description: "True 2-way systemic lipid biosynthesis inhibitor (LBI) moving both upward in xylem and downward in phloem.",
    crops: [
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Mealybugs & Thrips", dosage: 250, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Citrus",
        cropEmoji: "🍊",
        diseases: [
          { name: "Citrus Psyllid & Scales", dosage: 300, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Yellow Mites & Thrips", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Whitefly Nymphs & Thrips", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "thiodicarb-75-wp",
    name: "Thiodicarb 75% WP",
    category: "Insecticide",
    popularBrand: "Larvin / Checkmate",
    description: "Fast-acting carbamate ovicide and larvicide specialized against resistant Helicoverpa and Spodoptera.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Spodoptera litura & Bollworm", dosage: 400, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Tobacco Caterpillar & Semilooper", dosage: 300, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer", dosage: 300, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "triazophos-40-ec",
    name: "Triazophos 40% EC",
    category: "Insecticide",
    popularBrand: "Hostathion / Truzo",
    description: "Broad-spectrum contact organophosphate with translaminar penetration against whiteflies and leaf folders.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly & Spotted Bollworm", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Stem Borer & Leaf folder", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Girdle Beetle & Stem Fly", dosage: 350, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "chlorantraniliprole-thiamethoxam",
    name: "Chlorantraniliprole 18.5% + Thiamethoxam 25% WG",
    category: "Insecticide",
    popularBrand: "Voliam Flexi",
    description: "Premix combining ryanodine receptor activator with neonicotinoid systemic protection against borers and sucking pests.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Stem Borer & Brown Plant Hopper", dosage: 50, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer & Whitefly", dosage: 60, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bollworms, Aphids & Jassids", dosage: 60, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "flonicamid-50-wg",
    name: "Flonicamid 50% WG",
    category: "Insecticide",
    popularBrand: "Ulala / Beleaf",
    description: "Pyridinecarboxamide insecticide selectively paralyzing sucking pest mouthparts, stopping virus transmission.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly, Jassids & Aphids", dosage: 60, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown Plant Hopper (BPH)", dosage: 60, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips & Whiteflies", dosage: 60, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "pyriproxyfen-10-ec",
    name: "Pyriproxyfen 10% EC",
    category: "Insecticide",
    popularBrand: "Lano / Tiger / Epilock",
    description: "Juvenile hormone mimic inhibiting egg hatch and preventing whitefly and scale nymphs from becoming adults.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly Nymphs", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Whitefly & Scale Insects", dosage: 350, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "sulfoxaflor-21-8-sc",
    name: "Sulfoxaflor 21.8% SC",
    category: "Insecticide",
    popularBrand: "Transform / Closer",
    description: "Sulfoximine class insecticide providing rapid knockdown of resistant sap-feeding insects and plant hoppers.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown Plant Hopper (BPH)", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Jassids & Aphids", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "metaflumizone-22-sc",
    name: "Metaflumizone 22% SC",
    category: "Insecticide",
    popularBrand: "Verismo / Alverde",
    description: "Semicarbazone sodium-channel blocker delivering safe residual control of caterpillars and diamondback moth.",
    crops: [
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Diamondback Moth (DBM)", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Spodoptera & Fruit Borer", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "buprofezin-25-sc",
    name: "Buprofezin 25% SC",
    category: "Insecticide",
    popularBrand: "Applaud / Pointer",
    description: "Insect growth regulator stopping nymphal moulting of planthoppers, leafhoppers and whiteflies.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown Plant Hopper (BPH)", dosage: 330, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "White Backed Plant Hopper", dosage: 330, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly & Jassids", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Mango",
        cropEmoji: "🥭",
        diseases: [
          { name: "Mango Hopper", dosage: 450, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "alphacypermethrin-10-ec",
    name: "Alphacypermethrin 10% EC",
    category: "Insecticide",
    popularBrand: "Fastac / Stop / Alphaguard",
    description: "High-purity pyrethroid with rapid paralytic action against bollworms, borers and foliar caterpillars.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bollworms", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Stem Borer & Leaf folder", dosage: 110, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Semilooper & Girdle Beetle", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "quinalphos-25-ec",
    name: "Quinalphos 25% EC",
    category: "Insecticide",
    popularBrand: "Ekalux / Flash / Krush",
    description: "Broad-spectrum contact and stomach organophosphate with excellent leaf-penetrating action against leaf folders.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Rice Leaf folder", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Stem Borer & Hispa", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bollworms & Leaf roller", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Girdle Beetle & Pod Borer", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "monocrotophos-36-sl",
    name: "Monocrotophos 36% SL",
    category: "Insecticide",
    popularBrand: "Monocil / Phoskill / Luphos",
    description: "Fast-acting systemic organophosphate for piercing-sucking pests and leaf miners.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Aphids, Jassids & Bollworm", dosage: 450, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Yellow Stem Borer & Leaf folder", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Maize",
        cropEmoji: "🌽",
        diseases: [
          { name: "Shoot Fly & Stem Borer", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "bifenthrin-10-ec",
    name: "Bifenthrin 10% EC",
    category: "Insecticide",
    popularBrand: "Talstar / Markar / Brigade",
    description: "Multi-target pyrethroid insecticide-miticide with powerful soil repellency against termites and foliar borers.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bollworms & Whitefly", dosage: 320, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "Termites", dosage: 400, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Stem Borer & Leaf folder", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "abamectin-1-9-ec",
    name: "Abamectin 1.9% EC",
    category: "Insecticide",
    popularBrand: "Vertimec / Abacin",
    description: "Natural fermentation-derived avermectin providing superior translaminar activity against mites and leafminers.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Yellow Mites & Thrips", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Two-Spotted Spider Mite & Leaf Miner", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Thrips & Red Spider Mite", dosage: 180, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "lufenuron-5-4-ec",
    name: "Lufenuron 5.4% EC",
    category: "Insecticide",
    popularBrand: "Match / Cigna",
    description: "Benzoylurea insect growth regulator preventing chitin formation during caterpillar larval transitions.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Spodoptera litura", dosage: 240, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Diamondback Moth", dosage: 240, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Fruit Borer", dosage: 240, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "difenoconazole-25-ec",
    name: "Difenoconazole 25% EC",
    category: "Fungicide",
    popularBrand: "Score / Rubigan",
    description: "Broad-spectrum systemic triazole fungicide offering protective, curative, and eradicative activity.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Early Blight & Septoria Leaf Spot", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Anthracnose & Dieback", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
          { name: "Powdery Mildew", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Anthracnose & Powdery Mildew", dosage: 120, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight", dosage: 120, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "azoxystrobin-23-sc",
    name: "Azoxystrobin 23% SC",
    category: "Fungicide",
    popularBrand: "Amistar / Mirador / Azotrix",
    description: "Strobilurin broad-spectrum systemic fungicide inhibiting mitochondrial respiration with greening effect.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Blast & Sheath Blight", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Early & Late Blight", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Downy Mildew & Powdery Mildew", dosage: 200, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Anthracnose & Fruit Rot", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "kresoxim-methyl-44-3-sc",
    name: "Kresoxim-methyl 44.3% SC",
    category: "Fungicide",
    popularBrand: "Ergon / Stroby",
    description: "Quinolone outer-binding site strobilurin preventing fungal spore germination and mycelial growth.",
    crops: [
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Powdery Mildew", dosage: 150, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Powdery Mildew & Anthracnose", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight & Blast", dosage: 180, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "pyraclostrobin-20-wg",
    name: "Pyraclostrobin 20% WG",
    category: "Fungicide",
    popularBrand: "Headline / Opera",
    description: "Premium strobilurin with plant health booster, enhancing nitrate reductase activity and fungal defence.",
    crops: [
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Anthracnose & Cercospora Leaf Spot", dosage: 150, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Alternaria Leaf Spot & Grey Mildew", dosage: 150, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Tikka Leaf Spot & Rust", dosage: 150, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "picoxystrobin-22-52-sc",
    name: "Picoxystrobin 22.52% SC",
    category: "Fungicide",
    popularBrand: "Galileo",
    description: "Modern strobilurin with unique vapor activity and systemic redistribution protecting untreated leaf parts.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight", dosage: 240, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Rust & Frogeye Leaf Spot", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Maize",
        cropEmoji: "🌽",
        diseases: [
          { name: "Maydis Leaf Blight & Rust", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "fluxapyroxad-pyraclostrobin",
    name: "Fluxapyroxad 167 g/l + Pyraclostrobin 333 g/l SC",
    category: "Fungicide",
    popularBrand: "Priaxor",
    description: "SDHI and QoI dual-action premix protecting against leaf spots and ensuring exceptional physiological plant health.",
    crops: [
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Sheath Blight, Rust & Frogeye Spot", dosage: 80, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Corynespora & Alternaria Leaf Spot", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Tikka Leaf Spot", dosage: 80, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "tebuconazole-trifloxystrobin",
    name: "Trifloxystrobin 25% + Tebuconazole 50% WG",
    category: "Fungicide",
    popularBrand: "Nativo",
    description: "High-performing combination giving mesostemic and systemic fungal control with anti-lodging grain weight enhancement.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight, Blast & Dirty Panicle", dosage: 120, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Early Blight & Powdery Mildew", dosage: 140, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Mango",
        cropEmoji: "🥭",
        diseases: [
          { name: "Anthracnose & Powdery Mildew", dosage: 150, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Powdery Mildew & Fruit Rot", dosage: 140, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "boscalid-pyraclostrobin",
    name: "Boscalid 25.2% + Pyraclostrobin 12.8% WG",
    category: "Fungicide",
    popularBrand: "Signum / Bellis",
    description: "Specialized dual fungicide controlling Botrytis gray mold, Alternaria, and powdery mildews in high-value fruits.",
    crops: [
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Powdery Mildew & Botrytis Bunch Rot", dosage: 160, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Early Blight & Gray Mold", dosage: 160, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "fenamidone-mancozeb",
    name: "Fenamidone 10% + Mancozeb 50% WG",
    category: "Fungicide",
    popularBrand: "Sectin",
    description: "Oomycete specialist fungicide preventing zoospores release and curing late blight and downy mildew.",
    crops: [
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Late Blight", dosage: 500, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Late Blight & Buckeye Rot", dosage: 500, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Downy Mildew", dosage: 600, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "dimethomorph-50-wp",
    name: "Dimethomorph 50% WP",
    category: "Fungicide",
    popularBrand: "Acrobat / Mandi",
    description: "Cinnamic acid derivative stopping fungal cell wall synthesis in Peronosporales and Phytophthora.",
    crops: [
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Late Blight", dosage: 350, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Late Blight", dosage: 350, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Downy Mildew", dosage: 400, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "cymoxanil-mancozeb",
    name: "Cymoxanil 8% + Mancozeb 64% WP",
    category: "Fungicide",
    popularBrand: "Curzate M8",
    description: "Multi-site contact plus penetrant curative fungicide with quick anti-sporulant action on downy mildews.",
    crops: [
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Late Blight", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Late Blight", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Downy Mildew", dosage: 600, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "validamycin-3-l",
    name: "Validamycin 3% L",
    category: "Fungicide",
    popularBrand: "Sheathmar / Rhitovall",
    description: "Antibiotic fungicide produced by Streptomyces hygroscopicus explicitly curbing trehalase in Rhizoctonia solani.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Black Scurf (Rhizoctonia)", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "captan-50-wp",
    name: "Captan 50% WP",
    category: "Fungicide",
    popularBrand: "Captaf / Dhanutan",
    description: "Broad-spectrum phthalimide multi-site protective fungicide for foliar sprays and soil damping off.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Fruit Rot & Dieback", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Early Blight & Damping Off", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Early & Late Blight", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "propineb-70-wp",
    name: "Propineb 70% WP",
    category: "Fungicide",
    popularBrand: "Antracol",
    description: "Zinc-enriched dithiocarbamate contact fungicide providing broad protection plus bio-available zinc nutrition.",
    crops: [
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Early & Late Blight", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown Leaf Spot & Narrow Brown Leaf Spot", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Early Blight & Leaf Spot", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Dieback & Fruit Rot", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "isoprothiolane-40-ec",
    name: "Isoprothiolane 40% EC",
    category: "Fungicide",
    popularBrand: "Fuji-One",
    description: "Systemic blast cure fungicide with acropetal translocation stopping fungal appressoria penetration.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Leaf Blast & Neck Blast", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "fosetyl-al-80-wp",
    name: "Fosetyl-Al 80% WP",
    category: "Fungicide",
    popularBrand: "Aliette",
    description: "True ambimobile systemic phosphonate stimulating natural phytoalexin defense against Phytophthora rot and gummosis.",
    crops: [
      {
        cropName: "Citrus",
        cropEmoji: "🍊",
        diseases: [
          { name: "Gummosis & Foot Rot", dosage: 500, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Downy Mildew", dosage: 600, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "mandipropamid-23-4-sc",
    name: "Mandipropamid 23.4% SC",
    category: "Fungicide",
    popularBrand: "Revus",
    description: "Carboxylic acid amide (CAA) fungicide binding to leaf wax and preventing sporangia germination.",
    crops: [
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Late Blight", dosage: 160, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Late Blight", dosage: 160, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Downy Mildew", dosage: 160, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "fluopicolide-propamocarb",
    name: "Fluopicolide 6.25% + Propamocarb 62.5% SC",
    category: "Fungicide",
    popularBrand: "Infinito",
    description: "Translaminar and systemic anti-tubulin compound causing instant delocalization of spectrin-like proteins in oomycetes.",
    crops: [
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Late Blight", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Late Blight", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "carboxin-thiram",
    name: "Carboxin 37.5% + Thiram 37.5% WS",
    category: "Fungicide",
    popularBrand: "Vitavax Power",
    description: "Dual systemic and contact specialized seed treatment protecting against smuts, bunts and seedling rots.",
    crops: [
      {
        cropName: "Wheat",
        cropEmoji: "🌾",
        diseases: [
          { name: "Loose Smut & Seed Rot", dosage: 250, dosageUnit: "g/ac", waterAmount: 50, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Collar Rot & Damping Off", dosage: 250, dosageUnit: "g/ac", waterAmount: 50, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Seedling Blight & Root Rot", dosage: 200, dosageUnit: "g/ac", waterAmount: 50, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "bactrinashak-2-bromo-2-nitropropane",
    name: "2-Bromo-2-nitropropane-1,3-diol 95% SP",
    category: "Bactericide",
    popularBrand: "Bactronol / Bactrinashak",
    description: "Potent organic bactericide targeting bacterial cell walls and thiol groups to halt black arm and oily spot.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bacterial Blight / Black Arm (Xanthomonas)", dosage: 20, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Citrus",
        cropEmoji: "🍊",
        diseases: [
          { name: "Citrus Canker", dosage: 25, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Bacterial Spot & Canker", dosage: 20, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "copper-sulphate-lime-bordeaux",
    name: "Bordeaux Mixture (CuSO4 + Lime 1%)",
    category: "Bactericide",
    popularBrand: "Fresh Bordeaux Mixture / Copper Shield",
    description: "Traditional neutral copper sulphate and slaked lime complex protecting orchard trunks and foliage from cankers.",
    crops: [
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Bacterial Canker & Anthracnose", dosage: 1000, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Citrus",
        cropEmoji: "🍊",
        diseases: [
          { name: "Citrus Canker & Gummosis", dosage: 1200, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "oxytetracycline-hydrochloride",
    name: "Streptomycin Sulphate 9% + Tetracycline Hydrochloride 1%",
    category: "Bactericide",
    popularBrand: "Plantomycin / Agrimycin",
    description: "Systemic agricultural antibiotic combination inhibiting bacterial protein synthesis in plants.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Bacterial Leaf Blight (BLB)", dosage: 50, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bacterial Blight / Angular Leaf Spot", dosage: 40, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Bacterial Wilt & Spot", dosage: 40, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Citrus",
        cropEmoji: "🍊",
        diseases: [
          { name: "Citrus Canker", dosage: 50, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "chitosan-oligosaccharide-2",
    name: "Chitosan Oligosaccharide 2% SL",
    category: "Virucide",
    popularBrand: "Virastop / Bio-Shield V",
    description: "Bioactive elicitor that stimulates plant PR-protein synthesis and inhibits viral capsid assembly.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Chilli Leaf Curl Virus (ChiLCV)", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Tomato Leaf Curl Virus (ToLCV)", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Papaya",
        cropEmoji: "🍈",
        diseases: [
          { name: "Papaya Ring Spot Virus", dosage: 500, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "botanical-extract-virazole",
    name: "Herbal Antiviral Plant Extract Formulation",
    category: "Virucide",
    popularBrand: "V-Bind / Viro-Hit",
    description: "Phytochemical blend inducing systemic acquired resistance against geminiviruses and potyviruses.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Tomato Mosaic & Spotted Wilt Virus", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Murda Complex & Yellow Mosaic", dosage: 500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Banana",
        cropEmoji: "🍌",
        diseases: [
          { name: "Banana Bunchy Top Virus Vector Management", dosage: 600, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "salicylic-acid-derivative",
    name: "Salicylic Acid Elicitor 1% SL",
    category: "Virucide",
    popularBrand: "Immu-Plant / Resisto",
    description: "Systemic acquired resistance (SAR) trigger enhancing pathogenesis-related proteins to curb viral replication.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Leaf Curl & Mosaic Suppression", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Yellow Leaf Curl Virus", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "atrazine-50-wp",
    name: "Atrazine 50% WP",
    category: "Herbicide",
    popularBrand: "Atrataf / Dhanuzine",
    description: "Selective pre-emergence and early post-emergence herbicide for broadleaf and grassy weeds in maize and cane.",
    crops: [
      {
        cropName: "Maize",
        cropEmoji: "🌽",
        diseases: [
          { name: "Trianthema, Digitaria & Broadleaf Weeds", dosage: 600, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "Annual Grasses & Broadleaf Weeds", dosage: 800, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "metribuzin-70-wp",
    name: "Metribuzin 70% WP",
    category: "Herbicide",
    popularBrand: "Sencor / Tata Metri",
    description: "Photosystem II inhibitor for pre and post-emergence broadleaf and Phalaris minor control.",
    crops: [
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Chenopodium, Phalaris & Trianthema", dosage: 150, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "Broadleaf & Grassy Weeds", dosage: 300, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Wheat",
        cropEmoji: "🌾",
        diseases: [
          { name: "Phalaris minor & Broadleaf Weeds", dosage: 100, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Broadleaf Weeds (Pre-transplant)", dosage: 150, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "pyrazosulfuron-ethyl-10-wp",
    name: "Pyrazosulfuron Ethyl 10% WP",
    category: "Herbicide",
    popularBrand: "Saathi / Sempra Rice",
    description: "Early post-emergence sulfonylurea weedicide arresting ALS enzyme in sedges and broadleaf weeds in paddy.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Cyperus iria, Eclipta & Sedges", dosage: 80, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "halosulfuron-methyl-75-wg",
    name: "Halosulfuron Methyl 75% WG",
    category: "Herbicide",
    popularBrand: "Sempra / Dhanupra",
    description: "Premier selective herbicide specifically killing purple nutsedge (Motha / Cyperus rotundus) tubers.",
    crops: [
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "Purple Nutsedge (Cyperus rotundus / Motha)", dosage: 36, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Maize",
        cropEmoji: "🌽",
        diseases: [
          { name: "Cyperus rotundus", dosage: 36, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "oxyfluorfen-23-5-ec",
    name: "Oxyfluorfen 23.5% EC",
    category: "Herbicide",
    popularBrand: "Goal / Oxygold",
    description: "Pre-emergence diphenyl ether contact herbicide creating a chemical barrier layer preventing weed germination.",
    crops: [
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Chenopodium, Amaranthus & Annual Grasses", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Broadleaf Weeds & Annual Grasses", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Echinochloa & Commelina", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "fenoxaprop-p-ethyl-9-3-ec",
    name: "Fenoxaprop-p-ethyl 9.3% EC",
    category: "Herbicide",
    popularBrand: "Whip Super / Puma",
    description: "Selective post-emergence graminicide inhibiting ACCase in grassy weeds like Echinochloa without harming broadleaves.",
    crops: [
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Echinochloa, Digitaria & Barnyard Grass", dosage: 350, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Annual Grassy Weeds", dosage: 350, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Echinochloa crus-galli", dosage: 350, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "clodinafop-propargyl-15-wp",
    name: "Clodinafop Propargyl 15% WP",
    category: "Herbicide",
    popularBrand: "Topik / Point",
    description: "Specialized post-emergence wheat herbicide selectively destroying Phalaris minor (Gullidanda) and wild oats.",
    crops: [
      {
        cropName: "Wheat",
        cropEmoji: "🌾",
        diseases: [
          { name: "Phalaris minor (Canary Grass / Gullidanda)", dosage: 160, dosageUnit: "g/ac", waterAmount: 150, waterUnit: "l/ac" },
          { name: "Avena fatua (Wild Oat)", dosage: 160, dosageUnit: "g/ac", waterAmount: 150, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "quizalofop-ethyl-5-ec",
    name: "Quizalofop Ethyl 5% EC",
    category: "Herbicide",
    popularBrand: "Targa Super / Hakama",
    description: "Rapidly absorbed systemic grass weedkiller giving absolute safety to broadleaf crops like soybean and groundnut.",
    crops: [
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Echinochloa, Dinebra & Cynodon", dosage: 350, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Grassy Weeds", dosage: 350, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Grasses & Sedges", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Annual Grasses", dosage: 350, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "imazethapyr-10-sl",
    name: "Imazethapyr 10% SL",
    category: "Herbicide",
    popularBrand: "Pursuit / Lagao / Shaked",
    description: "Broad-spectrum early post-emergence imidazolinone for simultaneous grass and broadleaf weed control in pulses.",
    crops: [
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Echinochloa, Commelina & Trianthema", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Broadleaf Weeds & Grasses", dosage: 400, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "glufosinate-ammonium-13-5-sl",
    name: "Glufosinate Ammonium 13.5% SL",
    category: "Herbicide",
    popularBrand: "Basta / Sweep",
    description: "Non-selective contact herbicide inhibiting glutamine synthetase, offering safe directed spray in orchard inter-rows.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Mixed Weeds (Directed Inter-row)", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tea",
        cropEmoji: "🍵",
        diseases: [
          { name: "Broadleaf & Grassy Weeds", dosage: 1200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "paraquat-dichloride-24-sl",
    name: "Paraquat Dichloride 24% SL",
    category: "Herbicide",
    popularBrand: "Gramoxone / Allkill",
    description: "Fastest-acting non-selective contact desiccant destroying green plant tissue within hours of sunlight exposure.",
    crops: [
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Pre-emergence Weed Knockdown", dosage: 800, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Inter-row Weeds", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tea",
        cropEmoji: "🍵",
        diseases: [
          { name: "Annual & Perennial Weeds", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "butachlor-50-ec",
    name: "Butachlor 50% EC",
    category: "Herbicide",
    popularBrand: "Machete / Teer",
    description: "Standard pre-emergence chloroacetanilide for selective control of Echinochloa and sedges in transplanted rice.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Barnyard Grass (Echinochloa) & Sedges", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "oxadiargyl-80-wp",
    name: "Oxadiargyl 80% WP",
    category: "Herbicide",
    popularBrand: "Topstar",
    description: "Ultra-low-dose pre-emergence oxadiazole creating a surface barrier on wet paddy fields.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Annual Grasses, Sedges & Broadleaf Weeds", dosage: 35, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Pre-emergence Weeds", dosage: 35, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "fenpyroximate-5-ec",
    name: "Fenpyroximate 5% EC",
    category: "Acaricide",
    popularBrand: "Sedna / Mitigate",
    description: "Mitochondrial complex I electron transport inhibitor giving rapid knockdown of nymphs and adults of spider mites.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Yellow Mite (Polyphagotarsonemus latus)", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tea",
        cropEmoji: "🍵",
        diseases: [
          { name: "Red Spider Mite", dosage: 160, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "hexythiazox-5-45-ec",
    name: "Hexythiazox 5.45% EC",
    category: "Acaricide",
    popularBrand: "Maiden / Apollo",
    description: "Mite growth regulator (MGR) with strong ovicidal and larvicidal activity preventing mite resurgence.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Yellow Mite & Red Spider Mite Eggs", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Two-Spotted Spider Mite", dosage: 200, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "diafenthiuron-47-8-sc",
    name: "Diafenthiuron 47.8% SC",
    category: "Acaricide",
    popularBrand: "Pegasus SC / Polo SC",
    description: "Pro-insecticide photo-converted by UV rays into carbodiimide, killing whitefly nymphs and two-spotted mites.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly & Two-Spotted Spider Mite", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Mites & Thrips", dosage: 200, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "fosthiazate-10-g",
    name: "Fosthiazate 10% G",
    category: "Nematicide",
    popularBrand: "Nemathorin",
    description: "Non-fumigant organophosphate contact nematicide paralyzing infective juveniles of root-knot and cyst nematodes.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Root-Knot Nematode (Meloidogyne incognita)", dosage: 10000, dosageUnit: "g/ac", waterAmount: 0, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Potato Cyst Nematode (Globodera spp.)", dosage: 12000, dosageUnit: "g/ac", waterAmount: 0, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Banana",
        cropEmoji: "🍌",
        diseases: [
          { name: "Burrowing Nematode (Radopholus similis)", dosage: 12000, dosageUnit: "g/ac", waterAmount: 0, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "paecilomyces-lilacinus",
    name: "Purpureocillium lilacinum (Paecilomyces) 1% WP",
    category: "Nematicide",
    popularBrand: "Bio-Nematode / Paecil",
    description: "Beneficial bio-nematicidal fungus parasitizing nematode egg clutches and sedentary females in root galls.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Root-Knot Nematodes (Drench / Basal)", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Banana",
        cropEmoji: "🍌",
        diseases: [
          { name: "Corm Nematodes & Root-Knot", dosage: 1500, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Root-Knot Nematodes", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "fluensulfone-2-g",
    name: "Fluensulfone 2% G",
    category: "Nematicide",
    popularBrand: "Nimitz",
    description: "True nematicide causing irreversible metabolic exhaustion and mortality without harming beneficial earthworms.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Root-Knot Nematode", dosage: 8000, dosageUnit: "g/ac", waterAmount: 0, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Root-Knot & Lesion Nematode", dosage: 8000, dosageUnit: "g/ac", waterAmount: 0, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "trichoderma-viride-1-wp",
    name: "Trichoderma viride 1% WP (2x10^6 cfu/g)",
    category: "Bio-pesticide",
    popularBrand: "Bio-Derma / Niprot / Eco-Tricho",
    description: "Antagonistic beneficial fungus secreting cellulase and chitinase to colonize root zones and suppress soil pathogens.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Fusarium Wilt & Damping Off", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Damping Off & Root Rot", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Root Rot & Wilt (Rhizoctonia/Fusarium)", dosage: 1200, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Collar Rot & Seed Decay", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "trichoderma-harzianum-2-wp",
    name: "Trichoderma harzianum 2% WP",
    category: "Bio-pesticide",
    popularBrand: "Harzian-Shield / Bio-Cure-F",
    description: "Hyperparasitic bio-fungicide aggressively mycoparasitizing Sclerotium rolfsii, Rhizoctonia, and Pythium.",
    crops: [
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Stem Rot (Sclerotium rolfsii)", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Root Rot & Wilt", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Black Scurf & Dry Rot", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "pseudomonas-fluorescens-1-wp",
    name: "Pseudomonas fluorescens 1% WP",
    category: "Bio-pesticide",
    popularBrand: "Bio-Cure-B / Sudocel / Spot-Kill",
    description: "Plant growth-promoting rhizobacteria producing 2,4-DAPG antibiotics and siderophores inducing crop defense.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Bacterial Leaf Blight & Sheath Blight", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Bacterial Wilt (Ralstonia)", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Banana",
        cropEmoji: "🍌",
        diseases: [
          { name: "Panama Wilt (Fusarium)", dosage: 1500, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "beauveria-bassiana-1-15-wp",
    name: "Beauveria bassiana 1.15% WP",
    category: "Bio-pesticide",
    popularBrand: "Daman / Bio-Power / Boverin",
    description: "Entomopathogenic white muscardine fungus infecting target insects through the cuticle and multiplying haemolymph.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly, Thrips & Bollworm Larvae", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer & Whitefly", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips & Mites", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "metarhizium-anisopliae-1-wp",
    name: "Metarhizium anisopliae 1% WP",
    category: "Bio-pesticide",
    popularBrand: "Kalichakra / Bio-Magic",
    description: "Green muscardine bio-insecticide specializing in destroying subterranean soil grubs, termites and root borers.",
    crops: [
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "White Grub & Termites", dosage: 2000, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "White Grub (Holotrichia consanguinea)", dosage: 1500, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown Plant Hopper (BPH)", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "verticillium-lecanii-1-15-wp",
    name: "Lecanicillium (Verticillium) lecanii 1.15% WP",
    category: "Bio-pesticide",
    popularBrand: "Verticel / Mealy-Kill / Bio-Catch",
    description: "Specialized bio-pathogen of soft-bodied scale insects, aphids, mealybugs and whiteflies in humid canopies.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Mealybugs & Whitefly", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Grapevine Mealybug", dosage: 1200, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Whitefly & Aphids", dosage: 1000, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "bacillus-thuringiensis-var-kurstaki",
    name: "Bacillus thuringiensis var. kurstaki 8% WP",
    category: "Bio-pesticide",
    popularBrand: "Delfin / Dipel / Biolep",
    description: "Microbial biological crystal endotoxin forming pore perforations in caterpillar midguts, safe to bees and natural predators.",
    crops: [
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Diamondback Moth (DBM) & Cabbage Looper", dosage: 400, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer (Helicoverpa)", dosage: 400, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Spotted & American Bollworm", dosage: 500, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "nuclear-polyhedrosis-virus-ha-npv",
    name: "Helicoverpa armigera NPV (HaNPV 100 LE/ac)",
    category: "Bio-pesticide",
    popularBrand: "Helicide / HaNPV Bio",
    description: "Host-specific biological baculovirus causing lethal occlusion viral disease exclusively in Helicoverpa larvae.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Gram Pod Borer / Fruit Borer", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "American Bollworm", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "nuclear-polyhedrosis-virus-sl-npv",
    name: "Spodoptera litura NPV (SlNPV 100 LE/ac)",
    category: "Bio-pesticide",
    popularBrand: "Spodocide / SlNPV Bio",
    description: "Biological virus causing polyhedral nuclear destruction in tobacco caterpillars (Spodoptera litura).",
    crops: [
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Tobacco Caterpillar (Spodoptera)", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Armyworm / Spodoptera", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Foliage Defoliator Caterpillar", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "neem-azadirachtin-0-03-ec",
    name: "Azadirachtin 0.03% EC (300 ppm Neem Oil)",
    category: "Bio-pesticide",
    popularBrand: "Neem Gold / Nimbecidine 300",
    description: "Certified organic botanical repellent, anti-feedant, and oviposition deterrent for eco-friendly pest management.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Whitefly & Early Stage Borers", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips & Mites Repellency", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Brown Plant Hopper & Stem Borer", dosage: 1000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "neem-azadirachtin-5-ec",
    name: "Azadirachtin 5% EC (50,000 ppm)",
    category: "Bio-pesticide",
    popularBrand: "Fortune Aza / Neem Raj 50000",
    description: "High-concentration pure azadirachtin arresting ecdysone production with powerful zero-residue protection.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly, Thrips & Bollworm Instars", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips & Mites", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer & Pinworm (Tuta absoluta)", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "karanjin-extract-2-ec",
    name: "Karanj Oil Extract (Pongamia pinnata) 2% EC",
    category: "Bio-pesticide",
    popularBrand: "Derisom / Karanj Guard",
    description: "Natural furanoflavonoid bio-pesticide repellent disrupting insect spiracles and feeding instincts.",
    crops: [
      {
        cropName: "Citrus",
        cropEmoji: "🍊",
        diseases: [
          { name: "Citrus Psylla & Leaf Miner", dosage: 600, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Whitefly & Aphids", dosage: 600, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Mango",
        cropEmoji: "🥭",
        diseases: [
          { name: "Mango Hopper & Mealybug", dosage: 800, dosageUnit: "ml/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "bacillus-subtilis-1-wp",
    name: "Bacillus subtilis 1% WP (1x10^9 cfu/g)",
    category: "Bio-pesticide",
    popularBrand: "Serenade / Bio-Bac / Subtili-Shield",
    description: "Beneficial bio-bactericide forming protective lipopeptide biofilms preventing spore germination and soft rots.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Bacterial Spot & Early Blight", dosage: 800, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Potato",
        cropEmoji: "🥔",
        diseases: [
          { name: "Soft Rot & Common Scab", dosage: 800, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Grapes",
        cropEmoji: "🍇",
        diseases: [
          { name: "Powdery Mildew & Downy Mildew", dosage: 1000, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "dashaparni-ark",
    name: "Dashaparni Ark (10-Leaf Fermented Herbal Extract)",
    category: "Bio-pesticide",
    popularBrand: "Organic Desi Dashaparni / Prakritik Ark",
    description: "Traditional Vedic natural farming fermented preparation from 10 medicinal leaves for comprehensive pest deterring.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Sucking Pests & Early Bollworms", dosage: 2000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips, Mites & Leaf Curl", dosage: 2000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Stem Borer & Leaf Roller Repellency", dosage: 2000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "agniastra-herbal-spray",
    name: "Agniastra (Chilli-Garlic-Tobacco-Neem Decoction)",
    category: "Bio-pesticide",
    popularBrand: "Desi Agniastra Organic Spray",
    description: "Intense pungent bio-formulation based on capsaicin and allicin that eliminates hard-bodied borers naturally.",
    crops: [
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer & Caterpillars", dosage: 1500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Pink Bollworm & American Bollworm", dosage: 2000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Diamondback Moth & Cabbage Borer", dosage: 1500, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "jeevamrutha-foliar-spray",
    name: "Jeevamrutha (Filtered Microbial Bio-Culture)",
    category: "Bio-pesticide",
    popularBrand: "Prakritik Jeevamrutha Foliar",
    description: "Indigenous cow dung and urine microbial ferment delivering trillions of beneficial fungal and bacterial suppressors.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Foliar Blast & Sheath Rot Resistance", dosage: 5000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Wheat",
        cropEmoji: "🌾",
        diseases: [
          { name: "Rust & Smut Biological Defense", dosage: 5000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Early Blight & Wilt Resistance", dosage: 5000, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "spinosad-45-sc",
    name: "Spinosad 45% SC",
    category: "Insecticide",
    popularBrand: "Tracer / Success / Spintor",
    description: "Naturalyte macrocyclic lactone derived from Saccharopolyspora spinosa targeting nicotinic acetylcholine receptors.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips & Fruit Borer", dosage: 75, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bollworms & Thrips", dosage: 80, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer (Helicoverpa)", dosage: 70, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cabbage",
        cropEmoji: "🥬",
        diseases: [
          { name: "Diamondback Moth", dosage: 70, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "emamectin-lufenuron",
    name: "Emamectin Benzoate 1.5% + Lufenuron 7.5% WG",
    category: "Insecticide",
    popularBrand: "Proclaim Opti / Voliam Targo",
    description: "Knockdown avermectin coupled with insect growth regulator for complete eradication of Fall Armyworm and caterpillars.",
    crops: [
      {
        cropName: "Maize",
        cropEmoji: "🌽",
        diseases: [
          { name: "Fall Armyworm (Spodoptera frugiperda)", dosage: 80, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Spodoptera & Bollworms", dosage: 100, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer", dosage: 80, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "fipronil-imidacloprid",
    name: "Fipronil 40% + Imidacloprid 40% WG",
    category: "Insecticide",
    popularBrand: "Lesenta / Fipro-Imida",
    description: "High-concentration dual-mode systemic insecticide delivering unmatched protection against white grubs and root pests.",
    crops: [
      {
        cropName: "Sugarcane",
        cropEmoji: "🎋",
        diseases: [
          { name: "White Grub & Termites", dosage: 150, dosageUnit: "g/ac", waterAmount: 300, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "White Grub", dosage: 150, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Aphids, Jassids & Thrips", dosage: 100, dosageUnit: "g/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "thiamethoxam-lambda",
    name: "Thiamethoxam 12.6% + Lambda-cyhalothrin 9.5% ZC",
    category: "Insecticide",
    popularBrand: "Alika / Ampligo S",
    description: "Capsulated suspension (ZC) providing systemic sap-feeding pest elimination plus instantaneous contact knockdown.",
    crops: [
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Jassids, Aphids & Bollworms", dosage: 80, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Whitefly & Fruit Borer", dosage: 80, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips & Fruit Borer", dosage: 80, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Leafminer & Thrips", dosage: 80, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "chlorantraniliprole-lambdacyhalothrin",
    name: "Chlorantraniliprole 9.3% + Lambda-cyhalothrin 4.6% ZC",
    category: "Insecticide",
    popularBrand: "Ampligo / Voliam Duo",
    description: "Synergized ryanodine receptor activator and pyrethroid formulation destroying eggs, small larvae and large caterpillars.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Yellow Stem Borer & Leaf folder", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Maize",
        cropEmoji: "🌽",
        diseases: [
          { name: "Fall Armyworm (Spodoptera)", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "American & Spotted Bollworm", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "flubendiamide-thiacloprid",
    name: "Flubendiamide 19.92% + Thiacloprid 19.92% SC",
    category: "Insecticide",
    popularBrand: "Belt Expert",
    description: "Diamide and neonicotinoid combination simultaneously stopping shoot/fruit borers and vectoring sucking insects.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Thrips & Fruit Borer", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Fruit Borer & Whitefly", dosage: 100, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Cotton",
        cropEmoji: "☁️",
        diseases: [
          { name: "Bollworms, Aphids & Jassids", dosage: 120, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "difenoconazole-propiconazole",
    name: "Difenoconazole 15% + Propiconazole 15% EC",
    category: "Fungicide",
    popularBrand: "Taspa / Tiara",
    description: "Dual systemic triazole formulation providing broad preventive and curative control of sheath rot and dirty panicle.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight & Dirty Panicle", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Soybean",
        cropEmoji: "🫘",
        diseases: [
          { name: "Rust & Aerial Blight", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Tikka Leaf Spot & Rust", dosage: 150, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "azoxystrobin-tebuconazole",
    name: "Azoxystrobin 11% + Tebuconazole 18.3% SC",
    category: "Fungicide",
    popularBrand: "Custodia / Azoteb",
    description: "Strobilurin and triazole combination protecting crop foliage with systemic and translaminar disease eradication.",
    crops: [
      {
        cropName: "Chilli",
        cropEmoji: "🌶️",
        diseases: [
          { name: "Anthracnose & Powdery Mildew", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Tomato",
        cropEmoji: "🍅",
        diseases: [
          { name: "Early Blight", dosage: 250, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Onion",
        cropEmoji: "🧅",
        diseases: [
          { name: "Purple Blotch & Stemphylium Blight", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight & Blast", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
  {
    id: "kresoxim-methyl-thifluzamide",
    name: "Kresoxim-methyl 18% + Thifluzamide 5.4% SC",
    category: "Fungicide",
    popularBrand: "Pulsor Plus / Kreso-Thiflu",
    description: "Advanced combination providing immediate curative arrest of Rhizoctonia sheath blight and stem rot.",
    crops: [
      {
        cropName: "Rice",
        cropEmoji: "🌾",
        diseases: [
          { name: "Sheath Blight & Sheath Rot", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
      {
        cropName: "Groundnut",
        cropEmoji: "🥜",
        diseases: [
          { name: "Stem Rot (Sclerotium rolfsii)", dosage: 300, dosageUnit: "ml/ac", waterAmount: 200, waterUnit: "l/ac" },
        ],
      },
    ],
  },
];
