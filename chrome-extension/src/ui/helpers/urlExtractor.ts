/**
 * Extracts PR ID from Azure DevOps URL
 */
export function extractPRID(): string | null {
  const url = window.location.href;
  console.log('Current URL:', url);
  
  // Check if it's an Azure DevOps PR URL
  if (url.includes('dev.azure.com') && url.includes('/pullrequest/')) {
    // Extract PR ID using regex
    const match = url.match(/\/pullrequest\/(\d+)/);
    if (match && match[1]) {
      const prId = match[1];
      console.log('Extracted PR ID:', prId);
      
      // Send message to background script/popup
      chrome.runtime.sendMessage({ 
        action: 'prIdExtracted',
        prId 
      });
      
      return prId;
    }
  }
  
  return null;
}
