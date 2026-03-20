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

interface PlanningStore {
    sessionId: string | null;
    userId: string;
    nodes: Record<string, NodeState>;
    // actions
    initSession: (sessionId: string, userId: string, initialState: Record<string, NodeState>) => void;
    updateNodeFromSSE: (event: SSEEvent) => void;
    fetchState: (sessionId: string, userId: string) => Promise<void>;
    confirmNode: (nodeKey: string, data: any) => Promise<void>;
    lockNode: (nodeKey: string) => Promise<void>;
    unlockNode: (nodeKey: string) => Promise<void>;
    batchConfirm: () => Promise<void>;
    rollback: (nodeKey: string) => Promise<void>;
}

const API_BASE = "http://localhost:8000/api/v1/state";

export const usePlanningStore = create<PlanningStore>((set, get) => ({
    sessionId: null,
    userId: "user_123", // Default for now
    nodes: {},
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
    }
}));
