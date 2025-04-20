import { LANGGRAPH_API_URL } from '../config/constants';
import { getAssistantNameForThread } from '../threads';
import { getAssistantIdByName } from '../assistants';

// Make a request to the LangGraph API
export async function makeRequest(
  threadId: string, 
  prId: string, 
  isFollowUp = false, 
  followUpMessage = '',
  assistantId?: string, 
  customPrompt = ''
): Promise<Response> {
  // If no assistant ID is provided, try to get it from the thread's associated assistant name
  if (!assistantId) {
    const assistantName = getAssistantNameForThread(threadId);
    if (assistantName) {
      const id = await getAssistantIdByName(assistantName);
      if (id) assistantId = id;
    }
    
    // If still no assistant ID, fall back to PR editor (in case of error)
    if (!assistantId) {
      const editorId = await getAssistantIdByName('pr_editor');
      assistantId = editorId || ''; 
    }
  }
  
  // Prepare the request body
  let prompt = customPrompt;
  if (!prompt) {
    prompt = isFollowUp 
      ? followUpMessage
      : `Write a good pull request for the following PR ID: ${prId}`;
  }
  
  const messages = [{ content: prompt, type: "human" }];
  
  const requestBody = {
    input: {
      messages: messages
    },
    config: {
      configurable: {
        thread_id: threadId
      }
    },
    metadata: {
      from_studio: false,
      LANGGRAPH_API_URL: LANGGRAPH_API_URL
    },
    stream_mode: [
      "messages"
    ],
    stream_subgraphs: true,
    assistant_id: assistantId,
    interrupt_before: [],
    interrupt_after: [],
    multitask_strategy: "rollback"
  };
  
  return fetch(`${LANGGRAPH_API_URL}/threads/${threadId}/runs/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestBody)
  });
}
