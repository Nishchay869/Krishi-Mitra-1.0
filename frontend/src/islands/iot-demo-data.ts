export type FieldKey = 'all' | 'north' | 'east' | 'orchard'
export type Period = '24h' | '7d' | '30d'
export type Metric = 'moisture' | 'temperature' | 'humidity' | 'light'
export const fields = [
  { key: 'north', name: 'North field', crop: 'Rice', area: '2.4 ha', moisture: 64, temperature: 27.8, humidity: 74, light: 21.4 },
  { key: 'east', name: 'East field', crop: 'Tomato', area: '1.2 ha', moisture: 42, temperature: 29.4, humidity: 63, light: 25.8 },
  { key: 'orchard', name: 'Orchard', crop: 'Mango', area: '3.1 ha', moisture: 51, temperature: 28.2, humidity: 68, light: 23.1 },
] as const
export const devices = [
  { id: 'KM-SM-001', name: 'Soil probe 01', field: 'north', type: 'Soil moisture', status: 'Online', battery: 92, age: '2 min', signal: -61 },
  { id: 'KM-TH-002', name: 'Climate node 01', field: 'north', type: 'Temperature / humidity', status: 'Online', battery: 87, age: '2 min', signal: -65 },
  { id: 'KM-SM-003', name: 'Soil probe 02', field: 'east', type: 'Soil moisture', status: 'Online', battery: 78, age: '4 min', signal: -69 },
  { id: 'KM-TH-004', name: 'Climate node 02', field: 'east', type: 'Temperature / humidity', status: 'Low battery', battery: 18, age: '5 min', signal: -73 },
  { id: 'KM-SM-005', name: 'Soil probe 03', field: 'orchard', type: 'Soil moisture', status: 'Online', battery: 81, age: '3 min', signal: -66 },
  { id: 'KM-LX-006', name: 'Light sensor 01', field: 'orchard', type: 'Light intensity', status: 'Offline', battery: 54, age: '3 hr', signal: null },
] as const
export const metrics: Record<Metric, { label: string; unit: string; color: string; domain: [number, number]; description: string }> = {
  moisture: { label: 'Soil moisture', unit: '%', color: '#a3e635', domain: [0, 100], description: 'Illustrative soil moisture percentage; real values require sensor calibration.' },
  temperature: { label: 'Air temperature', unit: '°C', color: '#60a5fa', domain: [15, 40], description: 'Illustrative air temperature, not a weather forecast.' },
  humidity: { label: 'Relative humidity', unit: '%', color: '#c084fc', domain: [20, 100], description: 'Illustrative relative humidity samples.' },
  light: { label: 'Light intensity', unit: 'klx', color: '#fbbf24', domain: [0, 60], description: 'Illustrative illuminance; this is not a crop light prescription.' },
}
export function sampleSeries(field: FieldKey, period: Period) {
  const selected = fields.filter(item => field === 'all' || item.key === field)
  const mean = (metric: Metric) => selected.reduce((sum, item) => sum + item[metric], 0) / selected.length
  const count = period === '24h' ? 24 : period === '7d' ? 28 : 30
  return Array.from({ length: count }, (_, index) => {
    const wave = Math.sin(index * .42) + Math.cos(index * .19) * .6
    return {
      label: period === '24h' ? `${String(index).padStart(2, '0')}:00` : period === '7d' ? `Day ${Math.floor(index / 4) + 1}, ${String((index % 4) * 6).padStart(2, '0')}:00` : `Day ${index + 1}`,
      moisture: +(mean('moisture') + wave * 5 - index * .07).toFixed(1),
      temperature: +(mean('temperature') + Math.sin(index * .4 - 1.4) * 3.2).toFixed(1),
      humidity: +(mean('humidity') - wave * 5.5).toFixed(1),
      light: +(Math.max(0, mean('light') + Math.sin(index * .35 - 1.5) * 17)).toFixed(1),
    }
  })
}
