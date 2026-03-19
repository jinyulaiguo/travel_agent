import { create } from "zustand";

export type NodeStatus = "pending" | "generating" | "generated" | "confirmed" 
  | "rejected" | "stale" | "locked" | "skipped";

export interface NodeState {
    status: NodeStatus;
    data: any | null;
    lockedByUser: boolean;
}

export interface SSEEvent {
    type: string;
    node: string;
    status: NodeStatus;
    data?: any;
}

interface PlanningStore {
    sessionId: string | null;
    nodes: Record<string, NodeState>;
    // actions
    initSession: (sessionId: string, initialState: Record<string, NodeState>) => void;
    updateNodeFromSSE: (event: SSEEvent) => void;
    confirmNode: (nodeKey: string) => Promise<void>;
    rejectNode: (nodeKey: string, feedback: string) => Promise<void>;
    lockNode: (nodeKey: string) => void;
    rollback: (nodeKey: string) => Promise<void>;
}

export const usePlanningStore = create<PlanningStore>((set, get) => ({
    sessionId: null,
    nodes: {},
    initSession: (sessionId, initialState) => set({ sessionId, nodes: initialState }),
    updateNodeFromSSE: (event) => set((state) => ({
        nodes: {
            ...state.nodes, [event.node]: {
                ...state.nodes[event.node],
                status: event.status,
                data: event.data ?? state.nodes[event.node]?.data,
                lockedByUser: state.nodes[event.node]?.lockedByUser ?? false
            }
        }
    })),
    confirmNode: async (nodeKey) => {
        // Placeholder for confirmation API call
        console.log(`Confirming node: ${nodeKey}`);
    },
    rejectNode: async (nodeKey, feedback) => {
        // Placeholder for rejection API call
        console.log(`Rejecting node: ${nodeKey} with feedback: ${feedback}`);
    },
    lockNode: (nodeKey) => set((state) => ({
        nodes: {
            ...state.nodes, [nodeKey]: {
                ...state.nodes[nodeKey],
                lockedByUser: !state.nodes[nodeKey]?.lockedByUser
            }
        }
    })),
    rollback: async (nodeKey) => {
        // Placeholder for rollback API call
        console.log(`Rolling back node: ${nodeKey}`);
    }
}));
