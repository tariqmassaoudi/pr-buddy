import { LANGGRAPH_API_URL } from '../config/constants';

// Create a thread for the LangGraph API
export async function createThread(assistantName?: string): Promise<string | null> {
  try {
    const createThreadResponse = await fetch(`${LANGGRAPH_API_URL}/threads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        metadata: {}
      })
    });
    
    if (!createThreadResponse.ok) {
      throw new Error(`Failed to create thread: ${createThreadResponse.status}`);
    }
    
    const threadData = await createThreadResponse.json();
    const threadId = threadData.thread_id as string;
    
    if (!threadId) {
      throw new Error("Failed to get thread_id from API response");
    }
    
    // Store thread ID for future use
    localStorage.setItem('aiPrThreadId', threadId);
    
    // If an assistant name was provided, store it with the thread ID
    if (assistantName) {
      localStorage.setItem(`assistant_${threadId}`, assistantName);
    }
    
    console.log('Created new thread:', threadId);
    
    return threadId;
  } catch (error) {
    console.error('Error creating thread:', error);
    return null;
  }
}

// Get the assistant name associated with a thread
export function getAssistantNameForThread(threadId: string): string | null {
  return localStorage.getItem(`assistant_${threadId}`);
}
