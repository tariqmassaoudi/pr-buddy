import * as marked from 'marked';
import { UIUtil } from '../utils/dom';
import { CSS, MESSAGE_STYLES } from '../styles';

/**
 * Shows a user message bubble
 */
export function showUserMessage(message: string): void {
  const toolCallsList = UIUtil.getElementById<HTMLDivElement>('ai-tool-calls-list');
  if (!toolCallsList) return;
  
  // Create message wrapper
  const userMessage = UIUtil.createElement<HTMLDivElement>(
    'div', 
    'flex-row flex-end margin-top-8 margin-bottom-16'
  );
  
  // Create styled message container
  const messageContainer = UIUtil.createElement<HTMLDivElement>(
    'div', 
    '', 
    MESSAGE_STYLES.userMessage.container
  );
  
  // Create message text
  const messageSpan = UIUtil.createElement<HTMLSpanElement>('span', CSS.text.bodyS);
  messageSpan.textContent = message;
  
  // Assemble components
  messageContainer.appendChild(messageSpan);
  userMessage.appendChild(messageContainer);
  toolCallsList.appendChild(userMessage);
}

/**
 * Displays AI response with markdown support
 */
export function showAIResponse(message: string): void {
  const toolCallsList = UIUtil.getElementById<HTMLDivElement>('ai-tool-calls-list');
  if (!toolCallsList) return;
  
  // Get the current session ID to associate with this response
  const sessionId = toolCallsList.getAttribute('data-current-session') || '';
  
  // Remove "AI is responding" indicator if present
  const respondingIndicator = UIUtil.getElementById<HTMLDivElement>('ai-responding-indicator');
  if (respondingIndicator) {
    respondingIndicator.remove();
  }
  
  // Ensure markdown styles are present
  ensureMarkdownStyles();
  
  // Get or create the AI response element for this session
  let aiResponseElement = UIUtil.getElementById<HTMLDivElement>(`ai-response-${sessionId}`);
  if (!aiResponseElement) {
    // Create new response element
    aiResponseElement = createNewAIResponseElement(sessionId, message);
    toolCallsList.appendChild(aiResponseElement);
  } else {
    // Update existing response
    updateExistingAIResponse(aiResponseElement, message);
  }
}

/**
 * Creates a new AI response element
 */
function createNewAIResponseElement(sessionId: string, message: string): HTMLDivElement {
  // Create response wrapper
  const aiResponseElement = UIUtil.createElement<HTMLDivElement>(
    'div', 
    'flex-row flex-start margin-top-8 margin-bottom-16', 
    { width: '100%' }, 
    { id: `ai-response-${sessionId}` }
  );
  
  // Create response container
  const responseContainer = UIUtil.createElement<HTMLDivElement>(
    'div', 
    '', 
    MESSAGE_STYLES.aiResponse.container
  );
  
  // Create content div for markdown
  const contentDiv = UIUtil.createElement<HTMLDivElement>(
    'div', 
    'markdown-content body-s', 
    MESSAGE_STYLES.aiResponse.content
  );
  
  // Set content with markdown parsing
  contentDiv.innerHTML = message 
    ? marked.parse(message).toString() 
    : "I'm working on responding to your request...";
  
  // Assemble components
  responseContainer.appendChild(contentDiv);
  aiResponseElement.appendChild(responseContainer);
  
  return aiResponseElement;
}

/**
 * Updates an existing AI response
 */
function updateExistingAIResponse(aiResponseElement: HTMLDivElement, message: string): void {
  const contentDiv = aiResponseElement.querySelector('.markdown-content');
  if (contentDiv) {
    contentDiv.innerHTML = message 
      ? marked.parse(message).toString() 
      : "I'm working on responding to your request...";
  }
}

/**
 * Ensures markdown styles exist in the document
 */
function ensureMarkdownStyles(): void {
  UIUtil.addStyles('markdown-styles', MESSAGE_STYLES.markdownCss);
}
