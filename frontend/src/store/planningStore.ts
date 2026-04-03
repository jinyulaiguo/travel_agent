import { create } from "zustand";

export type NodeStatus = "pending" | "generating" | "generated" | "confirmed" 
  | "rejected" | "stale" | "locked" | "skipped";

export interface NodeState {
    status: NodeStatus;
    data: any | null;
    locked: boolean;
    compatibilityWarning?: string;
}

export interface IntentState {
    rawInput: string;
    parsing: boolean;
    result: any | null;
    confirmed: boolean;
}

export type StepStatus = "pending" | "isGenerating" | "confirmed";

interface PlanningStore {
    sessionId: string | null;
    userId: string;
    nodes: Record<string, NodeState>;
    intent: IntentState;
    
    // HIL Steps Management
    currentStep: number;
    stepStatus: Record<string, StepStatus>;
    
    // Actions
    initSession: (sessionId: string, userId: string, initialState: Record<string, NodeState>) => void;
    fetchState: (sessionId: string, userId: string) => Promise<void>;
    confirmNode: (nodeKey: string, data: any) => Promise<void>;
    lockNode: (nodeKey: string) => Promise<void>;
    unlockNode: (nodeKey: string) => Promise<void>;
    rollback: (nodeKey: string) => Promise<void>;
    
    // Intent Actions
    parseIntent: (text: string) => Promise<void>;
    confirmIntent: () => Promise<void>;
    setIntentResult: (result: any) => void;
    
    // HIL Specific Actions
    generateStep: (stepKey: string, endpoint: string, method?: string, body?: any) => Promise<any>;
    confirmStep: (stepKey: string, endpoint: string, body?: any) => Promise<any>;
    setStepStatus: (stepKey: string, status: StepStatus) => void;
    advanceStep: () => void;
    jumpToStep: (step: number) => void;
}

const API_BASE = "http://localhost:8000/api/v1";

export const STEP_KEYS = [
  "intent", 
  "flight", 
  "destination",
  "attraction", 
  "hotel", 
  "cost", 
  "schedule", 
  "export"
];

export const usePlanningStore = create<PlanningStore>((set, get) => ({
    sessionId: null,
    userId: "user_123", // Default for now
    nodes: {},
    intent: {
        rawInput: "",
        parsing: false,
        result: null,
        confirmed: false
    },
    
    currentStep: 0,
    stepStatus: {
        intent: "pending",
        flight: "pending",
        destination: "pending",
        attraction: "pending",
        hotel: "pending",
        cost: "pending",
        schedule: "pending",
        export: "pending",
    },

    initSession: (sessionId: string, userId: string, initialState: Record<string, NodeState>) => 
        set({ sessionId, userId, nodes: initialState }),

    fetchState: async (sessionId: string, userId: string) => {
        const res = await fetch(`${API_BASE}/state/${sessionId}?user_id=${userId}`);
        const data = await res.json();
        const newNodes: Record<string, NodeState> = {};
        Object.entries(data.nodes || {}).forEach(([key, val]: [string, any]) => {
            newNodes[key] = {
                status: val.status,
                data: val.data,
                locked: val.locked,
                compatibilityWarning: val.compatibility_warning
            };
        });
        set({ sessionId, userId, nodes: newNodes });
    },

    confirmNode: async (nodeKey: string, data: any) => {
        const { sessionId, userId } = get();
        await fetch(`${API_BASE}/state/${sessionId}/nodes/${nodeKey}/confirm?user_id=${userId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    },

    lockNode: async (nodeKey: string) => {
        const { sessionId, userId } = get();
        await fetch(`${API_BASE}/state/${sessionId}/nodes/${nodeKey}/lock?user_id=${userId}`, {
            method: 'POST'
        });
        set((state: PlanningStore) => ({
            nodes: {
                ...state.nodes, [nodeKey]: { ...state.nodes[nodeKey], locked: true, status: 'locked' }
            }
        }));
    },

    unlockNode: async (nodeKey: string) => {
        const { sessionId, userId } = get();
        await fetch(`${API_BASE}/state/${sessionId}/nodes/${nodeKey}/unlock?user_id=${userId}`, {
            method: 'POST'
        });
        set((state: PlanningStore) => ({
            nodes: {
                ...state.nodes, [nodeKey]: { ...state.nodes[nodeKey], locked: false, status: 'confirmed' }
            }
        }));
    },

    rollback: async (nodeKey: string) => {
        const { sessionId, userId } = get();
        await fetch(`${API_BASE}/state/${sessionId}/nodes/${nodeKey}/rollback?user_id=${userId}`, {
            method: 'POST'
        });
    },

    parseIntent: async (text: string) => {
        set({ intent: { ...get().intent, parsing: true, rawInput: text } });
        get().setStepStatus("intent", "isGenerating");
        try {
            const res = await fetch(`${API_BASE}/intent/parse`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_text: text,
                    current_intent: get().intent.result?.updated_intent || null
                })
            });
            const result = await res.json();
            set({ intent: { ...get().intent, parsing: false, result } });
            get().setStepStatus("intent", "pending"); // ready to confirm
            if (result.updated_intent?.session_id) {
                set({ sessionId: result.updated_intent.session_id });
            }
        } catch (error) {
            set({ intent: { ...get().intent, parsing: false } });
            get().setStepStatus("intent", "pending");
            console.error("Failed to parse intent:", error);
        }
    },

    setIntentResult: (result: any) => {
        set({ intent: { ...get().intent, result } });
    },

    confirmIntent: async () => {
        const { intent } = get();
        if (!intent.result?.updated_intent) return;
        
        get().setStepStatus("intent", "isGenerating");
        try {
            const res = await fetch(`${API_BASE}/intent/confirm`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(intent.result.updated_intent)
            });
            const confirmedIntent = await res.json();
            set({ intent: { ...intent, result: { ...intent.result, updated_intent: confirmedIntent }, confirmed: true } });
            get().setStepStatus("intent", "confirmed");
            get().advanceStep();
        } catch (error) {
            get().setStepStatus("intent", "pending");
            console.error("Failed to confirm intent:", error);
        }
    },

    generateStep: async (stepKey: string, endpoint: string, method: string = 'POST', body?: any) => {
        get().setStepStatus(stepKey, "isGenerating");
        try {
            const res = await fetch(`${API_BASE}${endpoint}`, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: body ? JSON.stringify(body) : undefined
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || `Failed to generate ${stepKey}`);
            }
            get().setStepStatus(stepKey, "pending");
            return data;
        } catch (error) {
            get().setStepStatus(stepKey, "pending");
            console.error(`Failed to generate ${stepKey}:`, error);
            throw error;
        }
    },

    confirmStep: async (stepKey: string, endpoint: string, body?: any) => {
        get().setStepStatus(stepKey, "isGenerating");
        try {
            const res = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: body ? JSON.stringify(body) : undefined
            });
            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.detail || `Failed to confirm ${stepKey}`);
            }
            get().setStepStatus(stepKey, "confirmed");
            get().advanceStep();
            return data;
        } catch (error) {
            get().setStepStatus(stepKey, "pending");
            console.error(`Failed to confirm ${stepKey}:`, error);
            throw error;
        }
    },

    setStepStatus: (stepKey: string, status: StepStatus) => {
        set((state) => ({
            stepStatus: { ...state.stepStatus, [stepKey]: status }
        }));
    },

    advanceStep: () => {
        const { currentStep } = get();
        if (currentStep < STEP_KEYS.length - 1) {
            set({ currentStep: currentStep + 1 });
        }
    },

    jumpToStep: (step: number) => {
        set({ currentStep: step });
    }
}));
