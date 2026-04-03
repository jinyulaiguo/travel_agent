import React, { useState, useEffect } from 'react';
import { usePlanningStore } from '../../../store/planningStore';

const IntentForm: React.FC = () => {
    const { intent, setIntentResult } = usePlanningStore();
    const data = intent.result?.updated_intent || {};
    
    // local state for editable fields
    const [origin, setOrigin] = useState(data.origin?.city || '');
    const [dest, setDest] = useState(data.destinations?.[0]?.city || '');
    const [depDate, setDepDate] = useState(data.departure_date || '');
    const [retDate, setRetDate] = useState(data.return_date || '');
    const [budget, setBudget] = useState(data.preferences?.budget?.total || '');
    const [travelers, setTravelers] = useState(data.travelers?.total || 1);
    
    useEffect(() => {
        setOrigin(data.origin?.city || '');
        setDest(data.destinations?.[0]?.city || '');
        setDepDate(data.departure_date || '');
        setRetDate(data.return_date || '');
        setBudget(data.preferences?.budget?.total || '');
        setTravelers(data.travelers?.total || 1);
    }, [data.origin?.city, data.destinations, data.departure_date, data.return_date, data.preferences?.budget?.total, data.travelers]);

    const handleBlur = () => {
        if (!intent.result) return;
        const newIntent = { ...intent.result };
        newIntent.updated_intent.origin = { ...newIntent.updated_intent.origin, city: origin };
        newIntent.updated_intent.destinations = [{ ...newIntent.updated_intent.destinations?.[0], city: dest }];
        newIntent.updated_intent.departure_date = depDate;
        newIntent.updated_intent.return_date = retDate;
        newIntent.updated_intent.preferences = { 
            ...newIntent.updated_intent.preferences, 
            budget: { ...newIntent.updated_intent.preferences?.budget, total: budget } 
        };
        newIntent.updated_intent.travelers = { ...newIntent.updated_intent.travelers, total: travelers };
        setIntentResult(newIntent);
    };

    const isConfirmed = intent.confirmed;

    return (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '16px' }}>
            <div className="form-group">
                <label className="form-label">出发地</label>
                <input 
                    className="editable-input" 
                    value={origin} 
                    onChange={e => setOrigin(e.target.value)} 
                    onBlur={handleBlur}
                    readOnly={isConfirmed}
                    placeholder="例如: 北京"
                />
            </div>
            <div className="form-group">
                <label className="form-label">目的地</label>
                <input 
                    className="editable-input" 
                    value={dest} 
                    onChange={e => setDest(e.target.value)} 
                    onBlur={handleBlur}
                    readOnly={isConfirmed}
                    placeholder="例如: 上海"
                />
            </div>
            <div className="form-group">
                <label className="form-label">出发日期</label>
                <input 
                    type="date"
                    className="editable-input" 
                    value={depDate} 
                    onChange={e => setDepDate(e.target.value)} 
                    onBlur={handleBlur}
                    readOnly={isConfirmed}
                />
            </div>
            <div className="form-group">
                <label className="form-label">返回日期</label>
                <input 
                    type="date"
                    className="editable-input" 
                    value={retDate} 
                    onChange={e => setRetDate(e.target.value)} 
                    onBlur={handleBlur}
                    readOnly={isConfirmed}
                />
            </div>
            <div className="form-group">
                <label className="form-label">预算金额 (元)</label>
                <input 
                    type="number"
                    className="editable-input" 
                    value={budget} 
                    onChange={e => setBudget(e.target.value === '' ? '' : Number(e.target.value))} 
                    onBlur={handleBlur}
                    readOnly={isConfirmed}
                />
            </div>
            <div className="form-group">
                <label className="form-label">总人数</label>
                <input 
                    type="number"
                    className="editable-input" 
                    value={travelers} 
                    onChange={e => setTravelers(Number(e.target.value))} 
                    onBlur={handleBlur}
                    readOnly={isConfirmed}
                />
            </div>
        </div>
    );
};

export default IntentForm;
