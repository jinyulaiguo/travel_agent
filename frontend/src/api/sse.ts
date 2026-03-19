import { fetchEventSource } from "@microsoft/fetch-event-source";
import { usePlanningStore } from "../store/planningStore";

// Placeholder for getting auth token
function getToken(): string {
  return "placeholder-token";
}

export async function startPlanningSSE(sessionId: string) {
    const { updateNodeFromSSE } = usePlanningStore.getState();
    
    await fetchEventSource(`/api/v1/planner/session/${sessionId}/run`, {
        method: "POST",
        headers: { 
            "Authorization": `Bearer ${getToken()}`,
            "Content-Type": "application/json"
        },
        onmessage(event) {
            if (event.data) {
                const data = JSON.parse(event.data);
                updateNodeFromSSE(data);
            }
        },
        onerror(err) {
            console.error("SSE error:", err);
            throw err; // fetchEventSource will auto-reconnect unless we throw
        },
    });
}
