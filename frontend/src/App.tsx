import { useState, useEffect } from 'react'

interface RecommendationView {
  rank: number
  name: string
  cuisine: string
  rating: number
  estimated_cost: string
  explanation: string
  location?: string
  area?: string
}

interface PresentationResult {
  summary?: string
  recommendations: RecommendationView[]
  fallback_used: boolean
  debug_info?: Record<string, any>
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function App() {
  // Input fields state
  const [locations, setLocations] = useState<string[]>([])
  const [cuisines, setCuisines] = useState<string[]>([])
  const [selectedLocation, setSelectedLocation] = useState('')
  const [selectedCuisine, setSelectedCuisine] = useState('')
  const [budget, setBudget] = useState<'low' | 'medium' | 'high'>('medium')
  const [minRating, setMinRating] = useState(4.2)
  const [additionalNotes, setAdditionalNotes] = useState('')

  // UI Flow states
  const [loading, setLoading] = useState(false)
  const [connected, setConnected] = useState(true)
  const [results, setResults] = useState<PresentationResult | null>(null)
  const [formError, setFormError] = useState('')

  // Preloaded mock data matching the screenshot for the initial premium feel
  const initialRecommendations: RecommendationView[] = [
    {
      rank: 1,
      name: "Happy Endings",
      cuisine: "Continental, Asian",
      rating: 4.9,
      estimated_cost: "$$$",
      explanation: "Our sentiment analysis identifies a 40% surge in \"unmatched ambiance\" mentions this month. Combined with your preference for quiet fine dining, the secluded mezzanine level here makes it a top-tier recommendation.",
      area: "Bellandur"
    },
    {
      rank: 2,
      name: "The Salted Rim",
      cuisine: "Mexican Fusion",
      rating: 4.7,
      estimated_cost: "$$$",
      explanation: "Zomato cluster data indicates a strong correlation between users with your 'Fine Dining' history and this establishment's unique tequila pairing experience. AI confidence score: 88%.",
      area: "Indiranagar"
    }
  ]

  const mockSummary = "Based on your interest in Fine Dining in Indiranagar, I've prioritized spots with high culinary consistency and specific \"special occasion\" markers in recent review datasets. These 12 matches reflect a 94% alignment with your taste profile."

  // Fetch initial autocomplete options & verify connection
  useEffect(() => {
    const initData = async () => {
      try {
        const healthRes = await fetch(`${API_BASE}/api/health`)
        if (!healthRes.ok) throw new Error('Backend health check failing')
        
        setConnected(true)

        const [locRes, cuisRes] = await Promise.all([
          fetch(`${API_BASE}/api/locations`),
          fetch(`${API_BASE}/api/cuisines`)
        ])

        if (locRes.ok && cuisRes.ok) {
          const locs: string[] = await locRes.json()
          const cuiss: string[] = await cuisRes.json()
          setLocations(locs)
          setCuisines(cuiss)
        }
      } catch (err) {
        console.error('Error connecting to FastAPI backend:', err)
        setConnected(false)
      }
    }

    initData()
  }, [])

  // Check connection status
  const checkConnection = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/health`)
      if (res.ok) {
        setConnected(true)
        const [locRes, cuisRes] = await Promise.all([
          fetch(`${API_BASE}/api/locations`),
          fetch(`${API_BASE}/api/cuisines`)
        ])
        if (locRes.ok && cuisRes.ok) {
          setLocations(await locRes.json())
          setCuisines(await cuisRes.json())
        }
      }
    } catch {
      setConnected(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')
    setLoading(true)

    try {
      const payload = {
        location: selectedLocation || "Indiranagar",
        budget,
        cuisine: selectedCuisine || "Continental",
        min_rating: minRating,
        additional_notes: additionalNotes.trim() || null
      }

      const response = await fetch(`${API_BASE}/api/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error('API server returned a failure state.')
      }

      const data: PresentationResult = await response.json()
      setResults(data)
    } catch (err) {
      console.error('Failed to get recommendation:', err)
      setFormError('Could not contact the Zomato AI server. Make sure the backend is active.')
      setConnected(false)
    } finally {
      setLoading(false)
    }
  }

  // Curated premium images matching the layout screenshot
  const getRestaurantImage = (rank: number) => {
    if (rank === 1) {
      return "https://lh3.googleusercontent.com/aida-public/AB6AXuBaz8pOJYuQlwgbQa4iysXYducMymdPilPXf7JJJR9Gf3CFNx2MjwNzHqSjOQ1YTVtn9U6Wa74bIbQyQgC5Bz8PAks9gLtadE2ZFGMwMs9H9zz62xC9prgEe4ELMguqEyY-qXig8uNY81IUT-gVK5E3AVz_P0_l1nlWjMBV_WXoDIWSeTBblIzq78t6gdH-Lb-CaoXEwN0yd5PhognNOVDW7Bg7Ldc2zSQ8fwdPJQHWHTjWrcsKGddThdPdOToJBqTdrqL5wM2zwtp7"
    }
    return "https://lh3.googleusercontent.com/aida-public/AB6AXuAAY2T2DfesusVmQb4iyyoKCaX8TjXMql7lMF4MCU6PsGcGkeCcgPxw5Tot9jloMQNlxtp1lB0vKClrItdfXLXJCL31_oItfwoYaumoW4Ap_eIN2chYokwy-hkpr5CEUdkDn517Y1GZ2exch2VbWCo45mEU1na-CtcDFGqUDesYxlIBU7H9OxDFthBYcL7FBRs2qd0mULPsZOy-uUeek6-ohjjd2u5Plc_365xjOr17f_mlmUzVp5K4XLeyDohyPr4Rsnpv5BqUY7pd"
  }

  const activeRecommendations = results ? results.recommendations : initialRecommendations
  const activeSummary = results ? results.summary : mockSummary

  return (
    <div className="font-body-md text-body-md overflow-x-hidden min-h-screen flex flex-col justify-between">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 bg-surface/80 backdrop-blur-xl border-b border-white/10 h-20 shadow-sm px-6 lg:px-container-padding-desktop flex justify-between items-center w-full max-w-[1280px] mx-auto">
        <div className="flex flex-col">
          <h1 className="font-display text-headline-md bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent drop-shadow-[0_0_10px_rgba(249,115,22,0.3)]">
            🍽️ ZOMATO AI
          </h1>
        </div>
        
        <div className="flex items-center gap-4">
          <div 
            onClick={checkConnection}
            className="flex items-center bg-surface-container px-4 py-2 rounded-full border border-white/5 gap-2 cursor-pointer hover:bg-white/5 transition-all"
          >
            <span className="relative flex h-3 w-3">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${connected ? 'bg-emerald-400' : 'bg-red-400'} opacity-75`}></span>
              <span className={`relative inline-flex rounded-full h-3 w-3 ${connected ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
            </span>
            <span className="font-label-md text-on-surface">
              {connected ? 'API Connected' : 'API Offline'}
            </span>
          </div>
          <button 
            onClick={checkConnection}
            className="material-symbols-outlined text-primary hover:bg-white/5 p-2 rounded-full transition-all text-xl"
            title="Sync API connection"
          >
            sensors
          </button>
        </div>
      </header>

      {/* Main Grid Content */}
      <main className="max-w-[1280px] w-full mx-auto px-6 lg:px-container-padding-desktop py-stack-lg grid grid-cols-1 lg:grid-cols-12 gap-gutter flex-grow">
        
        {/* Sidebar Panel */}
        <section className="lg:col-span-4 flex flex-col gap-stack-md">
          <div className="glass-card rounded-xl p-stack-md flex flex-col gap-6">
            <h2 className="font-headline-md text-primary">Refine Search</h2>
            
            <form onSubmit={handleSubmit} className="flex flex-col gap-6">
              
              {/* Location Input */}
              <div className="flex flex-col gap-stack-sm">
                <label htmlFor="loc-in" className="font-label-md text-on-surface-variant">Neighborhood Location</label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">location_on</span>
                  <input 
                    id="loc-in"
                    list="loc-data"
                    className="w-full bg-surface-variant/40 border border-white/10 rounded-lg py-3 pl-10 pr-4 text-on-surface placeholder:text-on-surface-variant/50 focus:ring-1 focus:ring-primary"
                    placeholder="e.g. Indiranagar, Bangalore" 
                    type="text"
                    value={selectedLocation}
                    onChange={(e) => setSelectedLocation(e.target.value)}
                  />
                  <datalist id="loc-data">
                    {locations.map((loc) => <option key={loc} value={loc} />)}
                  </datalist>
                </div>
              </div>

              {/* Budget pills */}
              <div className="flex flex-col gap-stack-sm">
                <label className="font-label-md text-on-surface-variant">Budget Segment</label>
                <div className="flex flex-wrap gap-2">
                  <button 
                    type="button"
                    onClick={() => setBudget('low')}
                    className={`px-4 py-2 rounded-full border ${budget === 'low' ? 'border-primary text-primary' : 'border-white/10 bg-surface-variant/40 text-on-surface-variant'} font-label-md hover:border-primary transition-all`}
                  >
                    Low Budget
                  </button>
                  <button 
                    type="button"
                    onClick={() => setBudget('medium')}
                    className={`px-4 py-2 rounded-full border ${budget === 'medium' ? 'border-primary text-primary' : 'border-white/10 bg-surface-variant/40 text-on-surface-variant'} font-label-md hover:border-primary transition-all`}
                  >
                    Medium
                  </button>
                  <button 
                    type="button"
                    onClick={() => setBudget('high')}
                    className={`px-4 py-2 rounded-full border ${budget === 'high' ? 'border-primary text-primary' : 'border-white/10 bg-surface-variant/40 text-on-surface-variant'} font-label-md hover:border-primary transition-all`}
                  >
                    High
                  </button>
                </div>
              </div>

              {/* Cuisine Preferences */}
              <div className="flex flex-col gap-stack-sm">
                <label htmlFor="cui-in" className="font-label-md text-on-surface-variant">Cuisine Preference</label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant">restaurant_menu</span>
                  <input 
                    id="cui-in"
                    list="cui-data"
                    className="w-full bg-surface-variant/40 border border-white/10 rounded-lg py-3 pl-10 pr-4 text-on-surface placeholder:text-on-surface-variant/50 focus:ring-1 focus:ring-primary"
                    placeholder="Search cuisines..." 
                    type="text"
                    value={selectedCuisine}
                    onChange={(e) => setSelectedCuisine(e.target.value)}
                  />
                  <datalist id="cui-data">
                    {cuisines.map((cui) => <option key={cui} value={cui} />)}
                  </datalist>
                </div>
              </div>

              {/* Rating Slider */}
              <div className="flex flex-col gap-stack-sm">
                <div className="flex justify-between items-center">
                  <label htmlFor="rat-in" className="font-label-md text-on-surface-variant">Minimum Rating</label>
                  <span className="bg-primary px-3 py-1 rounded-full text-on-primary font-bold text-label-md glow-orange" id="rating-val">
                    {minRating.toFixed(1)}
                  </span>
                </div>
                <input 
                  id="rat-in"
                  className="w-full h-2 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary" 
                  max="5" 
                  min="0" 
                  step="0.1" 
                  type="range" 
                  value={minRating}
                  onChange={(e) => setMinRating(parseFloat(e.target.value))}
                />
              </div>

              {/* Custom AI directives */}
              <div className="flex flex-col gap-stack-sm">
                <label htmlFor="dir-in" className="font-label-md text-on-surface-variant">Custom AI Directives</label>
                <textarea 
                  id="dir-in"
                  className="w-full bg-surface-variant/40 border border-white/10 rounded-lg p-3 text-on-surface resize-none focus:ring-1 focus:ring-primary" 
                  placeholder="e.g. Must have outdoor seating and good for large groups..." 
                  rows={3}
                  value={additionalNotes}
                  onChange={(e) => setAdditionalNotes(e.target.value)}
                />
              </div>

              {/* CTA button */}
              <button 
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-[#f97316] to-[#ef4444] text-white font-headline-md py-4 rounded-xl shadow-[0_0_30px_rgba(249,115,22,0.4)] hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center gap-3 disabled:opacity-50 disabled:hover:scale-100"
              >
                <span className="material-symbols-outlined">auto_awesome</span>
                {loading ? 'Consulting Zomato...' : 'Find AI Recommendations'}
              </button>

            </form>
          </div>

          {/* Backend Offline banner matches exactly as shown in screenshot */}
          {!connected && (
            <div className="glass-card border-red-500/50 p-4 rounded-xl flex items-start gap-3 bg-red-500/5 mt-4 transition-all">
              <span className="material-symbols-outlined text-red-500 mt-1">error</span>
              <div className="flex flex-col">
                <p className="font-label-md text-red-400 font-bold">FastAPI REST API Backend Offline</p>
                <p className="text-label-sm text-red-300/70">Connect local client or run 'make run-backend' to sync live Zomato clusters.</p>
              </div>
            </div>
          )}

          {formError && (
            <div className="text-red-400 text-sm font-semibold text-center p-3 rounded-lg border border-red-500/20 bg-red-500/5">
              {formError}
            </div>
          )}
        </section>

        {/* Main canvas and results */}
        <section className="lg:col-span-8 flex flex-col gap-stack-lg">
          
          {/* AI Curator insight banner */}
          {activeSummary && (
            <div className="relative overflow-hidden glass-card rounded-2xl p-stack-lg border-primary/20 bg-primary/5">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl -mr-10 -mt-10"></div>
              <div className="flex flex-col gap-stack-sm relative z-10">
                <div className="flex items-center gap-2 text-primary">
                  <span className="material-symbols-outlined">psychology</span>
                  <h3 className="font-headline-md">AI Curator Insight</h3>
                </div>
                <p className="font-body-lg text-on-surface opacity-90 leading-relaxed">
                  {activeSummary}
                </p>
              </div>
            </div>
          )}

          {/* Recommendations Cards list */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-gutter">
            
            {loading ? (
              // Shimmer loaders when submitting searches
              <>
                <div className="glass-card rounded-2xl overflow-hidden p-0 h-[380px] opacity-40">
                  <div className="shimmer w-full h-48"></div>
                  <div className="p-stack-md flex flex-col gap-stack-md">
                    <div className="shimmer h-8 w-3/4 rounded-lg"></div>
                    <div className="flex gap-2">
                      <div className="shimmer h-4 w-12 rounded-lg"></div>
                      <div className="shimmer h-4 w-24 rounded-lg"></div>
                    </div>
                    <div className="shimmer h-16 w-full rounded-xl mt-2"></div>
                  </div>
                </div>
                <div className="glass-card rounded-2xl overflow-hidden p-0 h-[380px] opacity-40">
                  <div className="shimmer w-full h-48"></div>
                  <div className="p-stack-md flex flex-col gap-stack-md">
                    <div className="shimmer h-8 w-1/2 rounded-lg"></div>
                    <div className="flex gap-2">
                      <div className="shimmer h-4 w-12 rounded-lg"></div>
                      <div className="shimmer h-4 w-24 rounded-lg"></div>
                    </div>
                    <div className="shimmer h-16 w-full rounded-xl mt-2"></div>
                  </div>
                </div>
              </>
            ) : (
              activeRecommendations.map((rec) => (
                <div key={rec.rank} className="group relative glass-card rounded-2xl overflow-hidden hover:scale-[1.02] transition-all duration-300">
                  <div className="relative h-48 overflow-hidden">
                    <img 
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" 
                      src={getRestaurantImage(rec.rank)}
                      alt={rec.name}
                    />
                    <div className={`absolute top-4 left-4 ${rec.rank === 1 ? 'bg-primary text-on-primary' : 'bg-surface-container-high text-on-surface border border-white/10'} px-3 py-1 rounded-full font-bold shadow-lg`}>
                      #{rec.rank} Rank
                    </div>
                  </div>
                  
                  <div className="p-stack-md flex flex-col gap-stack-sm">
                    <h4 className="font-headline-md text-on-surface">
                      {rec.name} · {rec.area || 'Bangalore'}
                    </h4>
                    
                    <div className="flex flex-wrap gap-2 items-center">
                      <span className="flex items-center gap-1 text-primary-fixed-dim font-bold">
                        <span className="material-symbols-outlined text-[18px]">star_border</span>
                        {rec.rating}
                      </span>
                      <span className="w-1 h-1 rounded-full bg-on-surface-variant/30"></span>
                      <span className="text-on-surface-variant font-label-md">
                        {rec.cuisine}
                      </span>
                      <span className="w-1 h-1 rounded-full bg-on-surface-variant/30"></span>
                      <span className="text-primary-fixed-dim font-label-md">
                        {rec.estimated_cost}
                      </span>
                    </div>

                    {/* Collapsible Explanations matches exactly */}
                    <div className="mt-4 border border-primary/20 rounded-xl bg-primary/5 p-3">
                      <details className="group/ai">
                        <summary className="list-none flex justify-between items-center cursor-pointer select-none">
                          <span className="font-label-md text-primary flex items-center gap-2">
                            <span className="material-symbols-outlined text-[20px]">auto_awesome</span>
                            Why this match?
                          </span>
                          <span className="material-symbols-outlined text-primary group-open/ai:rotate-180 transition-transform">expand_more</span>
                        </summary>
                        <div className="mt-3 text-label-md text-on-surface-variant leading-snug border-t border-primary/10 pt-2">
                          {rec.explanation}
                        </div>
                      </details>
                    </div>

                  </div>
                </div>
              ))
            )}



          </div>
        </section>

      </main>

      {/* Footer bar */}
      <footer className="w-full flex flex-col md:flex-row justify-between items-center px-6 lg:px-container-padding-desktop border-t border-outline-variant/20 py-stack-lg mt-stack-lg bg-surface-container-lowest">
        <div className="flex flex-col gap-2 mb-4 md:mb-0 text-center md:text-left">
          <span className="font-display text-label-md text-on-surface-variant uppercase tracking-wider">
            © 2024 GASTRO AI - PRECISION GASTRONOMY
          </span>
          <p className="text-label-sm text-on-surface-variant/50">
            Built with Groq LPU™ &amp; Zomato Real-time Feed
          </p>
        </div>
        <div className="flex gap-stack-md">
          <a className="font-label-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Privacy Policy</a>
          <a className="font-label-sm text-on-surface-variant hover:text-primary transition-colors" href="#">API Status</a>
          <a className="font-label-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Support</a>
          <a className="font-label-sm text-on-surface-variant hover:text-primary transition-colors" href="#">Terms</a>
        </div>
      </footer>
    </div>
  )
}

export default App
