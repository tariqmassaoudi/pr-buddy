import { UIUtil } from '../utils/dom';
import { ButtonClickHandler } from '../utils/types';
import { CSS } from '../styles';

/**
 * Creates a button with Azure DevOps styling
 */
export function createAIButton(id: string, text: string, clickHandler: ButtonClickHandler): HTMLElement {
  // Create a new container for our button
  const buttonContainer = UIUtil.createElement<HTMLDivElement>('div', CSS.button.container, { marginLeft: '8px' });

  // Create the button with the same styling as Azure DevOps buttons
  const button = UIUtil.createElement<HTMLButtonElement>('button', CSS.button.main, {}, {
    role: 'button',
    type: 'button',
    id,
    tabIndex: 0
  });

  // Add the text to the button
  const buttonText = UIUtil.createElement<HTMLSpanElement>('span', CSS.text.bodyM);
  buttonText.textContent = text;
  button.appendChild(buttonText);

  // Add click event listener
  button.addEventListener('click', clickHandler);

  // Add the button to the container
  buttonContainer.appendChild(button);
  
  return buttonContainer;
}

/**
 * Button state management utilities
 */
export const ButtonState = {
  // Disable a button by ID
  disable(buttonId: string): void {
    const button = UIUtil.getElementById<HTMLButtonElement>(buttonId);
    if (button) button.classList.add('disabled');
  },
  
  // Enable a button by ID
  enable(buttonId: string): void {
    const button = UIUtil.getElementById<HTMLButtonElement>(buttonId);
    if (button) button.classList.remove('disabled');
  }
};

// Export button state functions with original names for backward compatibility
export const disableButton = ButtonState.disable;
export const enableButton = ButtonState.enable;
