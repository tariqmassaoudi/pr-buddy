import { UIUtil } from '../utils/dom';
import { ANIMATIONS, SESSION_STYLES, STATUS_COLORS, ICONS } from '../styles';
import { CSS } from '../styles';
import { SessionStatus } from '../utils/types';

/**
 * Adds a tool call to the list
 */
export function addToolCall(name: string, params: Record<string, any> = {}, newSession = false): void {
  const toolCallsList = UIUtil.getElementById<HTMLDivElement>('ai-tool-calls-list');
  if (!toolCallsList) return;
  
  // Format the parameters for display
  const paramsText = formatToolCallParams(params);
  
  if (newSession) {
    addNewSessionToolCall(toolCallsList, name, paramsText);
  } else {
    updateExistingSession(toolCallsList, name, paramsText);
  }
}

/**
 * Formats parameters for display
 */
function formatToolCallParams(params: Record<string, any>): string {
  if (Object.keys(params).length === 0) return '';
  
  const displayParams = Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== '')
    .map(([key, value]) => `${key}: ${typeof value === 'string' ? value : JSON.stringify(value)}`)
    .join(', ');
  
  return displayParams ? ` (${displayParams})` : '';
}

/**
 * Adds a new session tool call
 */
function addNewSessionToolCall(toolCallsList: HTMLElement, name: string, paramsText: string): void {
  // Create a new session ID and store it
  const sessionId = `session-${Date.now()}`;
  toolCallsList.setAttribute('data-current-session', sessionId);
  
  // Reset previous current session indicators
  const oldCurrentBoxes = document.querySelectorAll('.current-session-box');
  oldCurrentBoxes.forEach(box => box.classList.remove('current-session-box'));
  
  // Create progress indicator
  const progressIndicator = UIUtil.createElement<HTMLDivElement>(
    'div',
    'flex-column margin-bottom-16 padding-8 current-session-box',
    SESSION_STYLES.progressIndicator,
    {
      id: `ai-tool-progress-${sessionId}`,
      'data-session-id': sessionId
    }
  );
  
  // Add stage indicator
  const stageIndicator = UIUtil.createElement<HTMLDivElement>(
    'div',
    CSS.panel.flexRow,
    {},
    { id: `ai-tool-stage-${sessionId}` }
  );
  
  stageIndicator.innerHTML = `
    <span class="fluent-icons-enabled" style="display: inline-block; animation: rotating 2s linear infinite;">
      <span aria-hidden="true" class="flex-noshrink fabric-icon ms-Icon--SyncStatus small" style="color: white;"></span>
    </span>
    <span class="body-s" style="color: white;">${name}${paramsText}</span>
  `;
  
  // Add loading indicator
  const loadingIndicator = UIUtil.createElement<HTMLDivElement>(
    'div',
    'loading-pulse',
    SESSION_STYLES.loadingIndicator,
    { id: `ai-loading-indicator-${sessionId}` }
  );
  
  // Add steps tracker
  const stepsTracker = UIUtil.createElement<HTMLDivElement>(
    'div',
    `margin-top-8 ${CSS.text.bodyXs}`,
    SESSION_STYLES.stepsTracker,
    { 
      id: `ai-tool-steps-${sessionId}`,
      'data-steps': name 
    }
  );
  stepsTracker.textContent = name;
  
  // Add animation styles if needed
  ensureAnimationStylesExist();
  
  // Assemble the components
  progressIndicator.appendChild(stageIndicator);
  progressIndicator.appendChild(loadingIndicator);
  progressIndicator.appendChild(stepsTracker);
  toolCallsList.appendChild(progressIndicator);
}

/**
 * Updates an existing session with a new tool call
 */
function updateExistingSession(toolCallsList: HTMLElement, name: string, paramsText: string): void {
  const sessionId = toolCallsList.getAttribute('data-current-session') || '';
  
  if (!sessionId) {
    // If no current session, create a new one
    addToolCall(name, {}, true);
    return;
  }
  
  const progressIndicator = UIUtil.getElementById<HTMLDivElement>(`ai-tool-progress-${sessionId}`);
  if (!progressIndicator) {
    // If we can't find the progress indicator, create a new session
    addToolCall(name, {}, true);
    return;
  }
  
  // Update the stage text
  const stageIndicator = UIUtil.getElementById<HTMLDivElement>(`ai-tool-stage-${sessionId}`);
  if (stageIndicator) {
    const stageText = stageIndicator.querySelector('span.body-s');
    if (stageText) {
      stageText.textContent = `${name}${paramsText}`;
    }
  }
  
  // Update steps tracker
  const stepsTracker = UIUtil.getElementById<HTMLDivElement>(`ai-tool-steps-${sessionId}`);
  if (stepsTracker) {
    // Get existing steps and append the new step
    let steps = stepsTracker.getAttribute('data-steps') || '';
    if (steps) steps += ' → ';
    steps += name;
    
    stepsTracker.setAttribute('data-steps', steps);
    stepsTracker.textContent = steps;
  }
}

/**
 * Ensures animation styles exist in the document
 */
function ensureAnimationStylesExist(): void {
  UIUtil.addStyles(ANIMATIONS.styleId, ANIMATIONS.keyframes);
}

/**
 * Updates the AI panel when complete
 */
export function completeToolCalls(threadId: string): void {
  const toolCallsList = UIUtil.getElementById<HTMLDivElement>('ai-tool-calls-list');
  if (!toolCallsList) return;
  
  const sessionId = toolCallsList.getAttribute('data-current-session') || '';
  if (!sessionId) return;
  
  updateSessionStatus(sessionId, 'success', 'Complete');
  
  // Add follow-up message input
  addFollowUpContainer(threadId);
}

/**
 * Signals an error in the tool calls
 */
export function showToolCallError(errorMessage: string): void {
  const toolCallsList = UIUtil.getElementById<HTMLDivElement>('ai-tool-calls-list');
  if (!toolCallsList) return;
  
  const sessionId = toolCallsList.getAttribute('data-current-session') || '';
  if (sessionId) {
    updateSessionStatus(sessionId, 'error', 'Failed');
  }
  
  // Add error message
  if (toolCallsList) {
    const errorElement = UIUtil.createElement<HTMLDivElement>(
      'div', 
      'flex-row flex-center rhythm-horizontal-8 margin-top-8 margin-bottom-8'
    );
    
    errorElement.innerHTML = `
      ${ICONS.warning}
      <span class="body-s" style="color: #a80000;">${errorMessage}</span>
    `;
    
    toolCallsList.appendChild(errorElement);
  }
}

/**
 * Helper function to update session status (success/error)
 */
function updateSessionStatus(sessionId: string, status: SessionStatus, statusText: string): void {
  const stageIndicator = UIUtil.getElementById<HTMLDivElement>(`ai-tool-stage-${sessionId}`);
  if (stageIndicator) {
    stageIndicator.innerHTML = `
      ${status === 'success' ? ICONS.success : ICONS.error}
      <span class="body-s" style="color: white;">${statusText}</span>
    `;
    
    // Update progress indicator background
    const progressIndicator = UIUtil.getElementById<HTMLDivElement>(`ai-tool-progress-${sessionId}`);
    if (progressIndicator) {
      progressIndicator.style.backgroundColor = status === 'success' ? 
        STATUS_COLORS.success : STATUS_COLORS.error;
      
      // Remove loading indicator
      const loadingIndicator = UIUtil.getElementById<HTMLDivElement>(`ai-loading-indicator-${sessionId}`);
      if (loadingIndicator) {
        loadingIndicator.remove();
      }
    }
  }
}

/**
 * Creates a tool progress container
 */
export function createToolProgress(sessionId: string): HTMLElement {
  const toolContainer = UIUtil.createElement<HTMLDivElement>(
    'div',
    'ai-tool-progress-container',
    {
      display: 'flex',
      flexDirection: 'column',
      padding: '8px 12px',
      border: '1px solid #e0e0e0',
      borderRadius: '4px',
      backgroundColor: '#fafafa',
      minHeight: '80px',
      margin: '4px 0',
      flexShrink: '0'
    }
  );

  // Create steps tracker
  const stepsContainer = UIUtil.createElement<HTMLDivElement>(
    'div',
    `ai-tool-steps-${sessionId}`,
    {
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
      marginTop: '8px',
      minHeight: '40px'
    }
  );

  toolContainer.appendChild(stepsContainer);
  return toolContainer;
}

// Import from followUp.ts to avoid circular dependencies
import { addFollowUpContainer } from '../components/followUp';
