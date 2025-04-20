import { makeRequest } from './api/requests';
import { processLangGraphEvent } from './api/utils/processor';
import { getAssistantIdByName } from './api/assistants';
import { getAssistantNameForThread, createThread } from './api/threads';
import { ASSISTANT_NAMES } from './api/config/constants';
import { addToolCall, completeToolCalls, showToolCallError } from './ui/components/toolCalls';
import { showAIResponse, showUserMessage } from './ui/components/messages';
import { setInputState } from './ui/components/followUp';

// Process a streaming response from the LangGraph API
export async function processStreamingResponse(
  response: Response, 
  callback?: (content: string) => void,
  isFollowUp: boolean = false
): Promise<string> {
  if (!response.ok || !response.body) {
    throw new Error(`API request failed with status: ${response.status}`);
  }

  // Process the streaming response
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let finalContent = '';
  let lastToolCall = '';
  
  // Variables to track event and data
  let currentEvent = '';
  let currentData = '';
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    // Decode the received chunk and add to buffer
    const chunk = decoder.decode(value, { stream: true });
    buffer += chunk;
    
    // Process lines in the buffer
    let lineEnd;
    while ((lineEnd = buffer.indexOf('\n')) !== -1) {
      const line = buffer.substring(0, lineEnd).trim();
      buffer = buffer.substring(lineEnd + 1);
      
      // Check if line is an event or data
      if (line.startsWith('event:')) {
        currentEvent = line;
      } else if (line.startsWith('data:')) {
        currentData = line.substring(5).trim(); // Remove 'data:' prefix
      }
      
      // Process if we have both event and data
      if (currentEvent && currentData) {
        try {
          const eventName = currentEvent.replace('event:', '').trim();
          const data = JSON.parse(currentData);
          
          // Extract tool call information if present
          if (eventName === 'messages/partial' && data[0]?.tool_calls?.length > 0) {
            const toolCall = data[0].tool_calls[0];
            const toolName = toolCall.name;
            
            // Only add if it's a new tool call
            if (toolName && toolName !== lastToolCall) {
              lastToolCall = toolName;
              addToolCall(toolName, toolCall.args, isFollowUp && lastToolCall === '');
            }
          }
          
          // Extract message content
          const content = processLangGraphEvent(eventName, data);
          if (content) {
            finalContent = content;
            if (callback) {
              callback(content);
            }
          }
          
          // Reset for next event
          currentEvent = '';
          currentData = '';
        } catch (error) {
          console.error("Error processing event and data:", error);
          
          // Don't reset if syntax error (might be incomplete data)
          if (!(error instanceof SyntaxError)) {
            currentEvent = '';
            currentData = '';
          }
        }
      }
    }
  }
  
  return finalContent;
}

// Generate PR with AI
export async function generatePRWithAI(prId: string): Promise<void> {
  try {
    // Create a new thread
    addToolCall('create_thread');
    
    // Use the PR editor assistant by name
    const threadId = await createThread(ASSISTANT_NAMES.PR_EDITOR);
    
    if (!threadId) {
      throw new Error("Failed to create thread");
    }
    
    // Get the assistant ID based on the name
    let assistantId: string | undefined = undefined;
    const id = await getAssistantIdByName(ASSISTANT_NAMES.PR_EDITOR);
    if (id) assistantId = id;
    
    // Make the request
    addToolCall('run_thread', { thread_id: threadId.substring(0, 8) + '...' });
    const response = await makeRequest(threadId, prId, false, '', assistantId);
    
    // Process the streaming response
    const finalContent = await processStreamingResponse(response);
    
    if (finalContent) {
      completeToolCalls(threadId);
    } else {
      showToolCallError("No content was generated. Please try again.");
    }
    
  } catch (error) {
    console.error('Error making LangGraph API request:', error);
    
    // Use the showToolCallError function to display the error
    const errorMessage = error instanceof Error ? error.message : String(error);
    showToolCallError(errorMessage);
  }
}

// Review PR with AI
export async function reviewPRWithAI(prId: string): Promise<void> {
  try {
    // Create a new thread
    addToolCall('create_thread');
    
    // Create thread with the review assistant name
    const threadId = await createThread(ASSISTANT_NAMES.PR_REVIEWER);
    
    if (!threadId) {
      throw new Error("Failed to create thread");
    }
    
    // Get the assistant ID based on name
    let assistantId: string | undefined = undefined;
    const id = await getAssistantIdByName(ASSISTANT_NAMES.PR_REVIEWER);
    if (id) assistantId = id;
    
    // Make the request using the review PR assistant
    addToolCall('analyze_pr', { thread_id: threadId.substring(0, 8) + '...', pr_id: prId });
    const response = await makeRequest(
      threadId, 
      prId, 
      false, 
      '', 
      assistantId,
      `Analyze and review the changes in PR #${prId}. Provide constructive feedback on code quality, potential issues, and suggestions for improvement.`
    );
    
    // Process the streaming response
    const finalContent = await processStreamingResponse(response);
    
    if (finalContent) {
      completeToolCalls(threadId);
    } else {
      showToolCallError("No review was generated. Please try again.");
    }
    
  } catch (error) {
    console.error('Error making LangGraph API request:', error);
    
    // Use the showToolCallError function to display the error
    const errorMessage = error instanceof Error ? error.message : String(error);
    showToolCallError(errorMessage);
  }
}

// Handle follow-up message
export async function handleFollowUpMessage(threadId: string, message: string): Promise<void> {
  // Show user message and disable input
  showUserMessage(message);
  setInputState(true);
  
  try {
    // Get the assistant name associated with this thread
    const assistantName = getAssistantNameForThread(threadId);
    
    // If we have an assistant name, get its ID
    let assistantId: string | undefined = undefined;
    if (assistantName) {
      const id = await getAssistantIdByName(assistantName);
      if (id) assistantId = id;
    }
    
    // Create new progress tracker for this follow-up session
    addToolCall('send_follow_up', { thread_id: threadId.substring(0, 8) + '...' }, true);
    
    // Make the request with the specific assistant ID if available
    const response = await makeRequest(threadId, '', true, message, assistantId);
    
    // Process the streaming response, updating the UI in real-time
    const finalContent = await processStreamingResponse(response, (content) => {
      showAIResponse(content);
    }, true);
    
    // Mark this follow-up session as complete
    if (finalContent) {
      completeToolCalls(threadId);
    }
    
    // Re-enable input when done
    setInputState(false);
  } catch (error) {
    console.error("Error sending follow-up message:", error);
    showToolCallError(error instanceof Error ? error.message : String(error));
    
    // Re-enable input on error
    setInputState(false);
  }
} 