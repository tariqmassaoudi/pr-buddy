import { UIUtil } from '../utils/dom';
import { CSS, PANEL_STYLES } from '../styles';

/**
 * Creates and injects the AI status panel for showing progress
 */
export function createAIStatusPanel(): HTMLElement {
  // Check if panel already exists
  const existingPanel = UIUtil.getElementById<HTMLDivElement>('ai-status-panel');
  if (existingPanel) return existingPanel;
  
  // Create panel container with Azure DevOps styling
  const panel = UIUtil.createElement<HTMLDivElement>('div', CSS.panel.container, PANEL_STYLES.panelStyles, {
    id: 'ai-status-panel'
  });
  
  // Create content area
  const content = UIUtil.createElement<HTMLDivElement>('div', CSS.panel.content, PANEL_STYLES.contentStyles);
  
  // Create tool calls container
  const toolCallsContainer = UIUtil.createElement<HTMLDivElement>(
    'div', 
    'ai-tool-calls-container', 
    PANEL_STYLES.toolCallsContainerStyles
  );
  
  // Create tool call header with integrated close button
  const toolCallsHeader = UIUtil.createElement<HTMLDivElement>(
    'div', 
    CSS.panel.flexRow, 
    PANEL_STYLES.headerStyles
  );
  
  const titleContainer = UIUtil.createElement<HTMLDivElement>('div', CSS.panel.flexRow);
  titleContainer.innerHTML = '<span class="fluent-icons-enabled"><span aria-hidden="true" class="flex-noshrink fabric-icon ms-Icon--Robot medium"></span></span><div class="logo" style="margin: 0 8px;"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><path d="M8 14s1.5 2 4 2 4-2 4-2" /><line x1="9" y1="9" x2="9.01" y2="9" /><line x1="15" y1="9" x2="15.01" y2="9" /></svg></div><span class="body-m">PR Buddy</span>';
  
  const closeButton = UIUtil.createElement<HTMLButtonElement>(
    'button', 
    CSS.button.iconButton, 
    PANEL_STYLES.closeButtonStyles
  );
  closeButton.innerHTML = '<span class="fluent-icons-enabled"><span aria-hidden="true" class="fabric-icon ms-Icon--Cancel small"></span></span>';
  closeButton.onclick = () => { panel.style.display = 'none'; };
  
  UIUtil.appendChildren(toolCallsHeader, [titleContainer, closeButton]);
  toolCallsContainer.appendChild(toolCallsHeader);
  
  // Create tool calls list
  const toolCallsList = UIUtil.createElement<HTMLDivElement>(
    'div', 
    CSS.panel.toolCallsList, 
    PANEL_STYLES.toolCallsListStyles, 
    { id: 'ai-tool-calls-list' }
  );
  
  toolCallsContainer.appendChild(toolCallsList);
  content.appendChild(toolCallsContainer);
  panel.appendChild(content);
  
  // Insert panel in the appropriate location
  injectPanelIntoPage(panel);
  
  return panel;
}

/**
 * Helper function to inject the panel into the page at an appropriate location
 */
function injectPanelIntoPage(panel: HTMLElement): void {
  // Find a good location - right after the PR description
  const prDescriptionCard = document.querySelector('.repos-pr-description-card');
  if (prDescriptionCard && prDescriptionCard.parentNode) {
    prDescriptionCard.parentNode.insertBefore(panel, prDescriptionCard.nextSibling);
    return;
  }

  // Fallback: insert before the activity feed
  const activityFeed = document.querySelector('.repos-activity-filter-dropdown');
  if (activityFeed && activityFeed.parentNode) {
    activityFeed.parentNode.insertBefore(panel, activityFeed);
    return;
  }

  // Last resort: just append to the page content
  const pageContent = document.querySelector('.page-content');
  if (pageContent) {
    pageContent.appendChild(panel);
  }
}

/**
 * Shows the status panel and resets content
 */
export function showAIStatusPanel(): void {
  const panel = createAIStatusPanel();
  panel.style.display = 'flex';
  
  // Clear previous content
  const toolCallsList = UIUtil.getElementById<HTMLDivElement>('ai-tool-calls-list');
  if (toolCallsList) {
    // Clear the list but keep any follow-up container
    const followUpContainer = UIUtil.getElementById<HTMLDivElement>('ai-follow-up-container');
    toolCallsList.innerHTML = '';
    
    if (followUpContainer) {
      panel.appendChild(followUpContainer);
    }
  }
}
