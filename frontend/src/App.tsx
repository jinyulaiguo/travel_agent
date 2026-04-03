import './App.css'
import { DisclaimerBanner } from './components/Confidence'
import IntentInput from './features/intent/components/IntentInput'
// Placeholders for future imports
import TransportSelection from './features/flight/components/TransportSelection'
import DestinationSelection from './features/destination/components/DestinationSelection'
import AttractionSelection from './features/attractions/components/AttractionSelection'
import HotelRecommendation from './features/hotel/components/HotelRecommendation'
import CostSummary from './features/cost/components/CostSummary'
import DailySchedule from './features/daily_schedule/components/DailySchedule'
import ExportPanel from './features/export/components/ExportPanel'

import { usePlanningStore } from './store/planningStore'

function App() {
  const { currentStep } = usePlanningStore();

  return (
    <>
      <header style={{ padding: '2rem 1rem', borderBottom: '1px solid var(--border)' }}>
        <h1 style={{ margin: 0, fontSize: '2.5rem' }}>Antigravity Travel</h1>
        <p style={{ color: 'var(--text)', marginTop: '0.5rem' }}>您的私人 AI 旅游规划专家</p>
      </header>

      <main style={{ padding: '2rem 1rem', minHeight: '60vh', maxWidth: '800px', margin: '0 auto' }}>
        
        {/* Step 0: Intent */}
        {currentStep >= 0 && (
           <section className="step-section">
             <IntentInput />
           </section>
        )}

        {/* Step 1: Flight / Transport */}
        {currentStep >= 1 && (
           <section className="step-section">
             <TransportSelection />
           </section>
        )}

        {/* Step 2: Destination Allocation */}
        {currentStep >= 2 && (
           <section className="step-section">
             <DestinationSelection />
           </section>
        )}

        {/* Step 3: Attractions */}
        {currentStep >= 3 && (
           <section className="step-section">
             <AttractionSelection />
           </section>
        )}

        {/* Step 4: Hotel */}
        {currentStep >= 4 && (
           <section className="step-section">
             <HotelRecommendation />
           </section>
        )}

        {/* Step 5: Cost Summary */}
        {currentStep >= 5 && (
           <section className="step-section">
             <CostSummary />
           </section>
        )}

        {/* Step 6: Schedule */}
        {currentStep >= 6 && (
           <section className="step-section">
             <DailySchedule />
           </section>
        )}

        {/* Step 7: Export */}
        {currentStep >= 7 && (
           <section className="step-section">
             <ExportPanel />
           </section>
        )}

      </main>

      <div className="ticks"></div>
      
      <footer style={{ padding: '2rem', borderTop: '1px solid var(--border)', marginTop: '4rem' }}>
        <DisclaimerBanner />
        <div style={{ marginTop: '2rem', color: 'var(--text)', fontSize: '14px', textAlign: 'center' }}>
          &copy; 2026 Antigravity Travel AI. All rights reserved.
        </div>
      </footer>
    </>
  )
}

export default App
