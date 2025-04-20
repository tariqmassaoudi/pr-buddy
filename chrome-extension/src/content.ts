/// <reference types="chrome" />

import { extractPRID } from './ui/helpers';
import { showAIStatusPanel, createAIStatusPanel } from './ui/components/panel';
import { createAIButton, disableButton, enableButton } from './ui/components/button';
import { generatePRWithAI, handleFollowUpMessage, reviewPRWithAI } from './handlers';

console.log('Chrome Extension Content Script Loaded');


// Function to inject AI buttons
function injectAIButtons() {
  const prId = extractPRID();
  if (!prId) return;

  // Find the Approve button container
  const approveButtonContainer = document.querySelector('.repos-pr-header-vote-button');
  if (!approveButtonContainer) {
    console.log('Approve button container not found');
    return;
  }

  // Check if our buttons already exist to avoid duplicates
  if (document.getElementById('ai-write-pr-button') || document.getElementById('ai-review-pr-button')) {
    return;
  }

  // Create "Write PR with AI" button
  const writeButton = createAIButton('ai-write-pr-button', 'Write PR with AI', () => {
    disableButton("ai-write-pr-button");
    showAIStatusPanel();
    generatePRWithAI(prId).finally(() => {
      enableButton("ai-write-pr-button");
    });
  });

  // Create "Review PR with AI" button
  const reviewButton = createAIButton('ai-review-pr-button', 'Review PR with AI', () => {
    disableButton("ai-review-pr-button");
    showAIStatusPanel();
    reviewPRWithAI(prId).finally(() => {
      enableButton("ai-review-pr-button");
    });
  });

  // Insert the buttons after the Approve button container
  approveButtonContainer.parentNode?.insertBefore(writeButton, approveButtonContainer.nextSibling);
  approveButtonContainer.parentNode?.insertBefore(reviewButton, writeButton.nextSibling);

  console.log('AI buttons injected successfully');
  
  // Create the AI status panel (hidden initially)
  createAIStatusPanel();
}

// Function to observe DOM changes for SPA navigation
function observeDOMChanges() {
  // Observer configuration
  const config = { childList: true, subtree: true };

  // Callback function for changes
  const callback = function(mutationsList: MutationRecord[]) {
    for (const mutation of mutationsList) {
      if (mutation.type === 'childList') {
        // Check if relevant elements have been added but our buttons aren't present
        if (document.querySelector('.repos-pr-header-vote-button') && 
            !document.getElementById('ai-write-pr-button') && 
            !document.getElementById('ai-review-pr-button')) {
          injectAIButtons();
        }
      }
    }
  };

  // Create and start observer
  const observer = new MutationObserver(callback);
  observer.observe(document.body, config);
}

// Set up event handlers
function setupEventHandlers() {
  // Handle follow-up message submissions
  document.addEventListener('sendFollowUp', ((event: CustomEvent) => {
    const { threadId, message } = event.detail;
    handleFollowUpMessage(threadId, message);
  }) as EventListener);
}

// Run when the page has loaded
window.addEventListener('load', () => {
  console.log('Page loaded, trying to inject AI buttons');
  // Wait a bit for the page to fully render its components
  setTimeout(() => {
    injectAIButtons();
    observeDOMChanges();
    setupEventHandlers();
  }, 1000);
});

// Also listen for URL changes
let lastUrl = window.location.href;
new MutationObserver(() => {
  const currentUrl = window.location.href;
  if (currentUrl !== lastUrl) {
    lastUrl = currentUrl;
    extractPRID();
    // Wait a bit for the page to fully render its components after URL change
    setTimeout(injectAIButtons, 1000);
  }
}).observe(document, { subtree: true, childList: true });

export {}; 