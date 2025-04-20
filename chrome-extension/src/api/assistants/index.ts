import { LANGGRAPH_API_URL } from '../config/constants';

// Cache for assistant IDs
let assistantIdsCache: Record<string, string> = {};

// Get assistant ID by name
export async function getAssistantIdByName(name: string): Promise<string | null> {
  // Check cache first
  if (assistantIdsCache[name]) {
    return assistantIdsCache[name];
  }
  
  try {
    const response = await fetch(`${LANGGRAPH_API_URL}/assistants/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
    });
    
    if (!response.ok) {
      throw new Error(`Failed to get assistants: ${response.status}`);
    }
    
    const assistants = await response.json();
    
    // Find the assistant with the matching name
    const assistant = assistants.find((a: any) => a.name === name);
    
    if (assistant && assistant.assistant_id) {
      // Store in cache for future use
      assistantIdsCache[name] = assistant.assistant_id;
      return assistant.assistant_id;
    }
    
    return null;
  } catch (error) {
    console.error(`Error getting assistant ID for ${name}:`, error);
    return null;
  }
}
