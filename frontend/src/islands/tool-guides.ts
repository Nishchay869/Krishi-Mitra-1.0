export interface ToolGuide {
  key: string
  title: string
  summary: string
  prepare: string[]
  steps: { title: string; text: string }[]
  example: string
  result: string
  button: string
}
export const toolGuides: ToolGuide[] = [
  {
    key: 'chat', title: 'Ask Assistant', summary: 'Turn a farming question into a conversation with useful context.',
    prepare: ['Your crop and growing stage', 'Village or district and recent field observations'],
    steps: [
      { title: 'Open the assistant', text: 'Choose Ask Assistant and sign in if prompted. The conversation screen has a message field and a Send button.' },
      { title: 'Describe your farm and question', text: 'Type in your preferred language. Include the crop, location, growth stage, and the problem or decision you need help with.' },
      { title: 'Send your message', text: 'Select Send and wait for the reply. If voice controls are available, you can dictate instead; check the transcribed words before sending.' },
      { title: 'Read the reply and its context', text: 'Look for the suggested next steps, any missing information, and a source when one is shown. Check whether the advice fits your field conditions.' },
      { title: 'Ask a focused follow-up', text: 'Add the requested details or ask the assistant to explain a step. Continue in the same conversation so your earlier context stays visible.' },
    ],
    example: '“I grow rice near Mysuru. The plants are at the tillering stage and lower leaves are yellowing. What should I observe before deciding what to do?”',
    result: 'A written conversation you can use to clarify the next question or field observation. Confirm consequential treatment or application decisions locally.', button: 'Start a conversation',
  },
  {
    key: 'crop', title: 'Crop Advisor', summary: 'Use soil and climate values to explore crops suited to your conditions.',
    prepare: ['A recent Soil Health Card or soil test', 'Temperature, humidity, soil pH, and rainfall values'],
    steps: [
      { title: 'Collect your measured inputs', text: 'Keep the soil report nearby. Find nitrogen, phosphorus, and potassium values and check that their units match the form’s kg/ha labels.' },
      { title: 'Enter soil nutrients', text: 'Open Crop Advisor and fill in Nitrogen (N), Phosphorus (P), and Potassium (K). Use the field labels to distinguish the three values.' },
      { title: 'Add your climate and pH', text: 'Enter temperature in °C, relative humidity in %, soil pH, and rainfall in mm. The page describes rainfall as expected seasonal rainfall; do not enter an irrigation dose.' },
      { title: 'Select Recommend crops', text: 'Review your values and submit the form. If a field is highlighted or an error appears, correct it and submit again.' },
      { title: 'Compare the recommendations', text: 'Read the recommended crops and displayed scores. Check growing conditions in the crop library and consider local water access, season, and market before choosing.' },
    ],
    example: 'Copy each soil-report value into the matching N, P, or K field, then add your local climate values. Avoid filling missing measurements with invented numbers.',
    result: 'A ranked list of recommended crops with model scores. These scores describe the model output; they are not a guarantee of suitability or harvest.', button: 'Open Crop Advisor',
  },
  {
    key: 'yield', title: 'Yield Estimate', summary: 'Explore an estimated harvest per hectare and, optionally, total production.',
    prepare: ['Crop, season, and state', 'Expected annual rainfall in mm', 'Optional farm area in hectares'],
    steps: [
      { title: 'Choose your crop', text: 'Open Yield Estimate and select a crop from the available list. The list contains the crops supported by this tool.' },
      { title: 'Select season and state', text: 'Choose the season and state that match the field you are planning for. Check both selections before continuing.' },
      { title: 'Enter rainfall and optional area', text: 'Fill in Expected annual rainfall (mm). Add farm area in hectares if you also want a total production estimate; leave the optional area blank for a per-hectare result.' },
      { title: 'Select Estimate yield', text: 'Submit the form. Resolve any missing-field or validation messages, then check that the result names the intended crop, season, and state.' },
      { title: 'Read the range and units', text: 'Review yield per hectare, the likely range, and total production when shown. Read historical and unusual-season notices. Cotton, jute, and mesta may use bales rather than tonnes.' },
    ],
    example: 'For a field measured in acres, convert to hectares before filling the optional area field. The form notes that 1 acre is approximately 0.405 ha.',
    result: 'A state-level yield estimate with a likely range and optional farm total. Actual yield can differ with variety, weather, soil, and management.', button: 'Open Yield Estimate',
  },
  {
    key: 'disease', title: 'Disease Check', summary: 'Send a leaf photo and field context for a clear, structured AI assessment.',
    prepare: ['One affected leaf', 'A sharp photo in good natural light'],
    steps: [
      { title: 'Prepare the leaf and background', text: 'Choose a single affected leaf and place it against a plain background. Keep the affected area visible without fingers or other leaves covering it.' },
      { title: 'Take a focused photo', text: 'Use indirect daylight and hold the camera steady. Fill the frame with the leaf while keeping its edges visible. Retake blurred or heavily shadowed images.' },
      { title: 'Add the photo and field context', text: 'Open Disease Check and choose your image. Add the crop name, location, growth stage, and how symptoms have changed. Review the disclosure: the photo and entered context are analyzed using advanced AI when you submit.' },
      { title: 'Select Analyze leaf', text: 'Submit the photo and wait for the AI to respond. If a configuration, quota, or connection message appears, follow that message; the page does not fall back to the local ML classifier.' },
      { title: 'Read the assessment and control steps', text: 'Review visible signs, possible causes, immediate non-chemical actions, prevention, and follow-up. Evidence strength is an AI estimate. Candidate chemical ingredients need local crop/target label verification; no spray dose is prescribed by the AI.' },
    ],
    example: 'A single leaf against a plain surface, photographed in indirect daylight, is more useful than a distant photo of several overlapping plants.',
    result: 'An AI-generated photo assessment with practical control steps. It is a starting point for investigation; confirm important treatment decisions with your local KVK.', button: 'Open Disease Check',
  },
  {
    key: 'weather', title: 'Weather & Advisory', summary: 'Find local forecast information and explore farm activity windows.',
    prepare: ['Village or town, district, and state', 'Current soil condition', 'Saved crops in your profile for crop-specific planning'],
    steps: [
      { title: 'Enter your location', text: 'Open Weather & Advisory and fill Village / town. Include district and state to help distinguish places with similar names.' },
      { title: 'Select soil condition', text: 'Choose Dry, Moist, or Wet based on the field you observe. Leave the selection unknown if you cannot assess it rather than guessing.' },
      { title: 'Select Get forecast', text: 'Submit the location and soil condition. Confirm the displayed location and forecast date. If prompted, add your village or select crops through your profile.' },
      { title: 'Read the forecast and crop plan', text: 'Review temperatures, rainfall, wind, and humidity. With saved crops, explore the crop plans and the spraying and irrigation time slots. Times are displayed locally.' },
      { title: 'Inspect an activity window', text: 'For spraying, select a time slot or Why this rating? to read the explanation. Compare the rating with actual field conditions and product-label requirements before acting.' },
    ],
    example: 'Enter “your village, district, state”, choose the observed soil condition, and check the forecast again before a weather-sensitive task.',
    result: 'A local forecast and, when crops and sufficient forecast data are available, activity-planning guidance. A suitable window is guidance, not permission to spray.', button: 'Open Weather & Advisory',
  },
  {
    key: 'market', title: 'Market Prices', summary: 'Compare published mandi prices and recent changes for your crop.',
    prepare: ['The state you want to compare', 'Your commodity name', 'Awareness of quality, transport, and local selling costs'],
    steps: [
      { title: 'Choose a state', text: 'Open Market Prices and select a state, or All India, from the state dropdown. The page refreshes to show the selected scope.' },
      { title: 'Check the publication date', text: 'Read Latest published and the comparison date before using the table. The latest available report can be older than today.' },
      { title: 'Find your commodity', text: 'When the price table is available, use Search crop to filter its rows. Clear the search to see the full list again.' },
      { title: 'Compare the columns', text: 'Read the latest and previous reported prices, change, and MSP where shown. The page quotes average modal prices in ₹ per quintal; missing values are shown as dashes.' },
      { title: 'Use the figures as a reference', text: 'Read the source note and compare the report with actual local offers. Allow for crop quality, variety, fees, and transport before deciding where to sell.' },
    ],
    example: 'Choose your state, search for your commodity, then compare the two reporting dates and the price-change column before contacting a buyer.',
    result: 'Published average modal prices across reporting mandis in the chosen scope. A local mandi or buyer may quote a different price.', button: 'Open Market Prices',
  },
  {
    key: 'fertilizer', title: 'Fertilizer Calculator', summary: 'Convert recommended nutrient rates into fertilizer product quantities.',
    prepare: ['Your crop and planting type', 'Field size and unit, or tree/plant count', 'A nutrient recommendation appropriate to your farm'],
    steps: [
      { title: 'Choose plants or trees', text: 'Open Fertilizer Calculator. Select Plants — field size for a field crop, or Trees — tree count when calculating for trees.' },
      { title: 'Select the crop preset', text: 'Choose the crop from the dropdown and select Go. Read the nutrient summary, source, region, and period. Defaults are regional guidance, not a soil test for your field.' },
      { title: 'Review or edit nutrient rates', text: 'Open Edit if you need to match your recommendation. Check the N–P2O5–K2O basis and units: these can be kg/ha, grams per tree, grams per plant, or grams per planting pit.' },
      { title: 'Enter area or count and calculate', text: 'For plants, enter Field size and Area unit; provide plant or pit count if requested. For trees, enter Number of trees. Select Calculate quantities.' },
      { title: 'Review products and application', text: 'Compare the calculated fertilizer combinations, product weights, and any excess-nitrogen notice. Select See application for the chosen combination. Check pack size and weigh the quantity rather than rounding to whole bags.' },
    ],
    example: 'For a field entered in acres, select Acres in Area unit. For a tree crop, switch to Trees and enter the tree count instead of reusing a field-area value.',
    result: 'Product quantities for the recommendation and planting size you entered. Timing, placement, and split doses still follow crop-specific local guidance.', button: 'Open Fertilizer Calculator',
  },
  {
    key: 'library', title: 'Crop Library', summary: 'Find crop references and read growing conditions, cultivation, and care.',
    prepare: ['A crop name or category', 'Your local growing context to compare with reference ranges'],
    steps: [
      { title: 'Open the library', text: 'Choose Crop Library to browse the grouped crop cards. Use All crops to start with the full collection.' },
      { title: 'Search or narrow the category', text: 'Enter a crop name in Search crop and submit. Use a category link to narrow the list; return to All crops to clear the category filter.' },
      { title: 'Open a crop card', text: 'Select the crop you want to read about. Check its common and scientific names so you are looking at the intended crop.' },
      { title: 'Read the reference sections', text: 'Explore Growing conditions, Cultivation, Soil parameters, and the crop-companion or rotation section. Check watering and drainage context rather than treating rainfall as an irrigation dose.' },
      { title: 'Follow the care and source links', text: 'Use Explore pests & diseases for the crop to investigate common issues. Open the cited sources when you need more context, and adjust general guidance to local variety and growth stage.' },
    ],
    example: 'Search for Rice, open its card, and compare the listed soil and climate guidance with your field before planning the season.',
    result: 'A crop reference with cultivation context and source links. Reference ranges are general guidance, not a prescription for every variety or location.', button: 'Explore Crop Library',
  },
]
