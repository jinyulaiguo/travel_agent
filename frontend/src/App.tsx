import './App.css'
import { DisclaimerBanner } from './components/Confidence'
import QuickModeButton from './components/common/QuickModeButton'
import IntentInput from './features/intent/components/IntentInput'
import TravelItinerary from './features/itinerary/components/TravelItinerary'
import { usePlanningStore } from './store/planningStore'

function App() {
  const { nodes, isPlanning } = usePlanningStore();
  
  // 计算当前生成的进度
  const nodeKeys = Object.keys(nodes);
  const totalNodes = 9; // L1 - L9
  const progress = Math.min(100, Math.round((nodeKeys.length / totalNodes) * 100));
  const isGenerating = nodeKeys.some(key => nodes[key].status === 'generating');

  const hasData = nodeKeys.length > 0;
  const showResults = hasData || isPlanning;

  return (
    <>
      <header style={{ padding: '2rem 1rem', borderBottom: '1px solid var(--border)' }}>
        <h1 style={{ margin: 0, fontSize: '2.5rem' }}>Antigravity Travel</h1>
        <p style={{ color: 'var(--text)', marginTop: '0.5rem' }}>您的私人 AI 旅游规划专家</p>
      </header>

      <main style={{ padding: '2rem 1rem', minHeight: '60vh' }}>
        {/* Step 1: Intent Input (L0) */}
        {!showResults ? (
          <section id="intent-phase">
            <IntentInput />
          </section>
        ) : (
          /* Step 2 & 3: Generation and Results (L1 - L9) */
          <section id="result-phase">
            {isGenerating && (
              <div style={{ 
                maxWidth: '600px', 
                margin: '2rem auto', 
                padding: '1rem', 
                background: 'var(--social-bg)',
                borderRadius: '12px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span>AI 正在全力为您规划... {progress}%</span>
                </div>
                <div style={{ 
                  width: '100%', 
                  height: '8px', 
                  background: 'var(--border)', 
                  borderRadius: '4px',
                  overflow: 'hidden'
                }}>
                  <div style={{ 
                    width: `${progress}%`, 
                    height: '100%', 
                    background: 'var(--accent)',
                    transition: 'width 0.5s ease-in-out'
                  }}></div>
                </div>
              </div>
            )}
            
            <TravelItinerary />
          </section>
        )}
      </main>

      <div className="ticks"></div>
      
      <footer style={{ padding: '2rem', borderTop: '1px solid var(--border)', marginTop: '4rem' }}>
        <DisclaimerBanner />
        <div style={{ marginTop: '2rem', color: 'var(--text)', fontSize: '14px' }}>
          &copy; 2026 Antigravity Travel AI. All rights reserved.
        </div>
      </footer>

      <QuickModeButton />
    </>
  )
}

export default App
