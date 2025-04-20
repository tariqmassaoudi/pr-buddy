// Extract content from a message
export function extractContentFromMessage(message: any): string | null {
  // Direct content case - most common
  console.log("extractContentFromMessage");
  console.log('message', message);
  console.log('message.type', message.type);
  console.log('message.content', message.content);
  if (message.type === 'ai' && typeof message.content === 'string' && message.content.trim() !== '') {
    return message.content;
  }
  
  // Tool calls with response data case
  if (message.additional_kwargs?.tool_responses) {
    const responses = message.additional_kwargs.tool_responses;
    if (Array.isArray(responses) && responses.length > 0) {
      // Try to get content from tool responses (could be nested)
      for (const response of responses) {
        if (typeof response.content === 'string' && response.content.trim() !== '') {
          return response.content;
        }
        // Try to parse content from stringified JSON
        if (typeof response.content === 'string') {
          try {
            const parsed = JSON.parse(response.content);
            if (parsed && typeof parsed.content === 'string') {
              return parsed.content;
            }
          } catch (e) {
            // Ignore parsing errors
          }
        }
      }
    }
  }
  
  // Handle case where content might be in the tool_call result
  if (message.additional_kwargs?.tool_call_result) {
    const result = message.additional_kwargs.tool_call_result;
    if (typeof result === 'string' && result.trim() !== '') {
      try {
        const parsed = JSON.parse(result);
        if (parsed && typeof parsed.content === 'string') {
          return parsed.content;
        }
        if (parsed && typeof parsed.result === 'string') {
          return parsed.result;
        }
      } catch (e) {
        // If not JSON, return the raw string
        return result;
      }
    }
  }
  
  return null;
}

// Process events from the LangGraph API
export function processLangGraphEvent(event: string, data: any): string | null {
  console.log(`Processing ${event} event`, data);
  
  let content: string | null = null;
  
  switch (event) {
    case 'messages':
    case 'messages/partial':
      console.log("inside the partial case");
      if (Array.isArray(data)) {
        // Handle array of messages
        for (const message of data) {
          let extractedContent = extractContentFromMessage(message);
          if (extractedContent) {
            content = extractedContent;
            break;
          }
        }
      } else if (data.messages && Array.isArray(data.messages)) {
        // Handle nested messages
        for (const message of data.messages) {
          const extractedContent = extractContentFromMessage(message);
          if (extractedContent) {
            content = extractedContent;
            break;
          }
        }
      }
      break;
      
    case 'tool_response':
      if (data.result) {
        content = typeof data.result === 'string' 
          ? data.result 
          : JSON.stringify(data.result, null, 2);
      }
      break;
      
    case 'tool_start':
    case 'tool_end':
      // Log but don't update content
      console.log(`${event} event:`, data);
      break;
      
    default:
      console.log(`Unhandled event type: ${event}`);
  }
  
  return content;
}
