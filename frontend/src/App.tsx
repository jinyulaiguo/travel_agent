import React, { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'
import HotelRecommendation from './features/hotel/components/HotelRecommendation'
import DailySchedule from './features/daily_schedule/components/DailySchedule'
import { DisclaimerBanner } from './components/Confidence'
import QuickModeButton from './components/common/QuickModeButton'
import ConfirmationGate from './components/common/ConfirmationGate'

import { usePlanningStore, type NodeState } from './store/planningStore'

function App() {
  const [count, setCount] = useState(0)
  const { initSession } = usePlanningStore();

  React.useEffect(() => {
    // Mock initialization for testing
    const mockNodes: Record<string, NodeState> = {
      "L4_hotel": { status: "generated", data: {}, locked: false },
      "L5_itinerary": { status: "generating", data: null, locked: false },
      "L6_transport": { status: "pending", data: null, locked: false },
    };
    initSession("test_session_123", "user_123", mockNodes);
    
    // In real app, we would fetch the actual state
    // fetchState("test_session_123", "user_123");
  }, []);

  const mockItinerary = {
    days: [
      {
        day: 1,
        date: "2026-03-20",
        total_active_hours: 6.5,
        has_conflicts: false,
        items: [
          {
            id: "1",
            type: "attraction",
            name: "故宫博物院",
            planned_start_time: "09:00",
            planned_end_time: "12:00",
            duration_hours: 3.0,
            notes: "建议早点出发"
          },
          {
            id: "2",
            type: "fixed_slot",
            name: "固定行程：午餐休息",
            planned_start_time: "12:00",
            planned_end_time: "13:30",
            duration_hours: 1.5
          },
          {
            id: "3",
            type: "attraction",
            name: "景山公园",
            planned_start_time: "14:00",
            planned_end_time: "15:30",
            duration_hours: 1.5,
            notes: "俯瞰故宫全景"
          },
          {
            id: "4",
            type: "buffer",
            name: "交通/休息",
            planned_start_time: "15:30",
            planned_end_time: "16:00",
            duration_hours: 0.5
          }
        ]
      },
      {
        day: 2,
        date: "2026-03-21",
        total_active_hours: 4.0,
        has_conflicts: false,
        items: [
          {
            id: "5",
            type: "attraction",
            name: "颐和园",
            planned_start_time: "09:00",
            planned_end_time: "13:00",
            duration_hours: 4.0
          }
        ]
      }
    ]
  };

  return (
    <>
      <section id="center">
        <div className="hero">
          <img src={heroImg} className="base" width="170" height="179" alt="" />
          <img src={reactLogo} className="framework" alt="React logo" />
          <img src={viteLogo} className="vite" alt="Vite logo" />
        </div>
        <div>
          <h1>Get started</h1>
          <p>
            Edit <code>src/App.tsx</code> and save to test <code>HMR</code>
          </p>
        </div>
        <button
          className="counter"
          onClick={() => setCount((count) => count + 1)}
        >
          Count is {count}
        </button>
      </section>

      <div className="ticks"></div>

      <section id="daily-schedule-module" style={{ padding: '40px 0' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '30px' }}>📅 每日行程编排测试</h2>
        <ConfirmationGate nodeKey="L5_itinerary" title="每日行程编排">
          <DailySchedule initialData={mockItinerary as any} />
        </ConfirmationGate>
      </section>

      <div className="ticks"></div>
      
      <section id="hotel-module" style={{ padding: '40px 0' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '30px' }}>🏨 酒店推荐测试</h2>
        <ConfirmationGate nodeKey="L4_hotel" title="酒店选择">
          <HotelRecommendation />
        </ConfirmationGate>
      </section>

      <div className="ticks"></div>
      <section id="spacer"></section>
      <DisclaimerBanner />
      <QuickModeButton />
    </>
  )
}

export default App
