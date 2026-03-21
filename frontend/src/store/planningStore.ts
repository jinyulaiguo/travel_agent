import { create } from "zustand";

export type NodeStatus = "pending" | "generating" | "generated" | "confirmed" 
  | "rejected" | "stale" | "locked" | "skipped";

export interface NodeState {
    status: NodeStatus;
    data: any | null;
    locked: boolean;
    compatibilityWarning?: string;
}

export interface SSEEvent {
    type: string;
    node: string;
    status: NodeStatus;
    data?: any;
}

export interface IntentState {
    rawInput: string;
    parsing: boolean;
    result: any | null;
    confirmed: boolean;
}

interface PlanningStore {
    sessionId: string | null;
    userId: string;
    nodes: Record<string, NodeState>;
    intent: IntentState;
    isPlanning: boolean;
    // actions
    initSession: (sessionId: string, userId: string, initialState: Record<string, NodeState>) => void;
    updateNodeFromSSE: (event: SSEEvent) => void;
    fetchState: (sessionId: string, userId: string) => Promise<void>;
    confirmNode: (nodeKey: string, data: any) => Promise<void>;
    lockNode: (nodeKey: string) => Promise<void>;
    unlockNode: (nodeKey: string) => Promise<void>;
    batchConfirm: () => Promise<void>;
    rollback: (nodeKey: string) => Promise<void>;
    // New actions
    parseIntent: (text: string) => Promise<void>;
    confirmIntent: () => Promise<void>;
    triggerPlanning: () => Promise<void>;
}

const API_BASE = "http://localhost:8000/api/v1/state";

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
    isPlanning: false,
    initSession: (sessionId: string, userId: string, initialState: Record<string, NodeState>) => 
        set({ sessionId, userId, nodes: initialState }),
    
    updateNodeFromSSE: (event: SSEEvent) => set((state: PlanningStore) => ({
        nodes: {
            ...state.nodes, [event.node]: {
                ...state.nodes[event.node],
                status: event.status,
                data: event.data ?? state.nodes[event.node]?.data,
                locked: state.nodes[event.node]?.locked ?? false
            }
        }
    })),

    fetchState: async (sessionId: string, userId: string) => {
        const res = await fetch(`${API_BASE}/${sessionId}?user_id=${userId}`);
        const data = await res.json();
        const newNodes: Record<string, NodeState> = {};
        Object.entries(data.nodes).forEach(([key, val]: [string, any]) => {
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
        await fetch(`${API_BASE}/${sessionId}/nodes/${nodeKey}/confirm?user_id=${userId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    },

    lockNode: async (nodeKey: string) => {
        const { sessionId, userId } = get();
        await fetch(`${API_BASE}/${sessionId}/nodes/${nodeKey}/lock?user_id=${userId}`, {
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
        await fetch(`${API_BASE}/${sessionId}/nodes/${nodeKey}/unlock?user_id=${userId}`, {
            method: 'POST'
        });
        set((state: PlanningStore) => ({
            nodes: {
                ...state.nodes, [nodeKey]: { ...state.nodes[nodeKey], locked: false, status: 'confirmed' }
            }
        }));
    },

    batchConfirm: async () => {
        const { sessionId, userId } = get();
        await fetch(`${API_BASE}/${sessionId}/batch-confirm?user_id=${userId}`, {
            method: 'POST'
        });
    },

    rollback: async (nodeKey: string) => {
        const { sessionId, userId } = get();
        await fetch(`${API_BASE}/${sessionId}/nodes/${nodeKey}/rollback?user_id=${userId}`, {
            method: 'POST'
        });
    },

    parseIntent: async (text: string) => {
        set({ intent: { ...get().intent, parsing: true, rawInput: text } });
        try {
            const res = await fetch(`http://localhost:8000/intent/parse?user_text=${encodeURIComponent(text)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(get().intent.result?.updated_intent || null)
            });
            const result = await res.json();
            set({ intent: { ...get().intent, parsing: false, result } });
            if (result.updated_intent?.session_id) {
                set({ sessionId: result.updated_intent.session_id });
            }
        } catch (error) {
            set({ intent: { ...get().intent, parsing: false } });
            console.error("Failed to parse intent:", error);
        }
    },

    confirmIntent: async () => {
        const { intent } = get();
        if (!intent.result?.updated_intent) return;
        
        try {
            const res = await fetch(`http://localhost:8000/intent/confirm`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(intent.result.updated_intent)
            });
            const confirmedIntent = await res.json();
            set({ intent: { ...intent, result: { ...intent.result, updated_intent: confirmedIntent }, confirmed: true } });
        } catch (error) {
            console.error("Failed to confirm intent:", error);
        }
    },

    triggerPlanning: async () => {
        const { sessionId, userId, isPlanning } = get();
        if (!sessionId || isPlanning) return;

        // Reset nodes for fresh generation
        set({ nodes: {}, isPlanning: true });

        const eventSource = new EventSource(`http://localhost:8000/api/v1/planner/session/${sessionId}/run?user_id=${userId}`);
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'node_status_change' || data.type === 'node_data_ready') {
                get().updateNodeFromSSE({
                    type: data.type,
                    node: data.node,
                    status: data.status || (data.type === 'node_data_ready' ? 'generated' : 'pending'),
                    data: data.data
                });
            } else if (data.type === 'planning_complete') {
                set({ isPlanning: false });
                eventSource.close();
            }
        };

        eventSource.onerror = () => {
            set({ isPlanning: false });
            eventSource.close();
        };
    }
}));
