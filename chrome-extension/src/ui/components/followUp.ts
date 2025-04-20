import { UIUtil } from '../utils/dom';
import { CSS, FOLLOW_UP_STYLES } from '../styles';

/**
 * Helper function to add follow-up container
 */
export function addFollowUpContainer(threadId: string): void {
  // Remove existing container if any
  const existingContainer = UIUtil.getElementById<HTMLDivElement>('ai-follow-up-container');
  if (existingContainer) {
    existingContainer.remove();
  }
  
  const panel = UIUtil.getElementById<HTMLDivElement>('ai-status-panel');
  if (!panel) return;
  
  // Create container
  const followUpContainer = UIUtil.createElement<HTMLDivElement>(
    'div',
    'flex-column separator-line-top padding-top-16 padding-16',
    FOLLOW_UP_STYLES.container,
    { id: 'ai-follow-up-container' }
  );
  
  // Create input row
  const followUpInput = UIUtil.createElement<HTMLDivElement>('div', CSS.panel.flexRow);
  
  // Create text input
  const textInput = UIUtil.createElement<HTMLInputElement>(
    'input',
    'bolt-textfield-input flex-grow padding-8 body-m',
    FOLLOW_UP_STYLES.input,
    {
      id: 'ai-follow-up-input',
      type: 'text',
      placeholder: 'Send a follow-up message...'
    }
  );
  
  // Add keypress event for Enter key
  textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendFollowUpMessage(threadId);
    }
  });
  
  // Create send button
  const sendButton = UIUtil.createElement<HTMLButtonElement>(
    'button',
    CSS.button.primary,
    {}
  );
  sendButton.innerHTML = `<span class="bolt-button-text ${CSS.text.bodyM}">Send</span>`;
  sendButton.onclick = () => sendFollowUpMessage(threadId);
  
  // Assemble components
  UIUtil.appendChildren(followUpInput, [textInput, sendButton]);
  followUpContainer.appendChild(followUpInput);
  panel.appendChild(followUpContainer);
}

/**
 * Helper function to send a follow-up message
 */
function sendFollowUpMessage(threadId: string): void {
  const input = UIUtil.getElementById<HTMLInputElement>('ai-follow-up-input');
  if (input && input.value.trim()) {
    const message = input.value.trim();
    const event = new CustomEvent('sendFollowUp', { 
      detail: { threadId, message } 
    });
    document.dispatchEvent(event);
    
    // Clear the input field
    input.value = '';
  }
}

/**
 * Enable/disable the input field
 */
export function setInputState(disabled: boolean): void {
  const input = UIUtil.getElementById<HTMLInputElement>('ai-follow-up-input');
  if (input) {
    input.disabled = disabled;
    if (!disabled) {
      input.value = '';
      input.focus();
    }
  }
  
  // Also disable/enable the send button
  const sendButton = document.querySelector('#ai-follow-up-container .bolt-button') as HTMLButtonElement;
  if (sendButton) {
    if (disabled) {
      sendButton.classList.add('disabled');
      sendButton.disabled = true;
    } else {
      sendButton.classList.remove('disabled');
      sendButton.disabled = false;
    }
  }
}
