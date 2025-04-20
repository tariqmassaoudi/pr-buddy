/**
 * Styles for user and AI message bubbles
 */
export const MESSAGE_STYLES = {
  userMessage: {
    container: {
      padding: '8px 12px',
      borderRadius: '8px',
      maxWidth: '80%',
      backgroundColor: 'rgba(0, 120, 212, 0.2)', // Blue-ish for user messages
      color: 'white',
      fontWeight: '500'
    }
  },
  aiResponse: {
    container: {
      padding: '8px 12px',
      borderRadius: '8px',
      maxWidth: '100%',
      width: '100%',
      backgroundColor: 'rgba(0, 0, 0, 0.1)',
      color: 'white',
      wordWrap: 'break-word',
      overflowWrap: 'break-word',
      minHeight: '50px'
    },
    content: {
      maxWidth: '100%',
      minHeight: '30px'
    }
  },
  markdownCss: `
    .markdown-content {
      color: white;
      font-size: 12px;
      line-height: 1.4;
      word-wrap: break-word;
      overflow-wrap: break-word;
      max-width: 100%;
    }
    .markdown-content code {
      background-color: rgba(0, 0, 0, 0.2);
      padding: 2px 4px;
      border-radius: 3px;
      font-family: monospace;
      font-size: 11px;
      white-space: pre-wrap;
      word-break: break-all;
    }
    .markdown-content pre {
      background-color: rgba(0, 0, 0, 0.2);
      padding: 8px;
      border-radius: 4px;
      overflow-x: auto;
      max-width: 100%;
    }
    .markdown-content pre code {
      background-color: transparent;
      padding: 0;
      white-space: pre-wrap;
      word-break: break-all;
    }
    .markdown-content h1, 
    .markdown-content h2, 
    .markdown-content h3, 
    .markdown-content h4, 
    .markdown-content h5, 
    .markdown-content h6 {
      margin-top: 12px;
      margin-bottom: 8px;
      font-weight: 600;
      color: white;
      display: block;
    }
    .markdown-content h1 { 
      font-size: 16px; 
      border-bottom: 1px solid rgba(255, 255, 255, 0.2);
      padding-bottom: 4px;
    }
    .markdown-content h2 { 
      font-size: 15px; 
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      padding-bottom: 3px;
    }
    .markdown-content h3 { font-size: 14px; }
    .markdown-content h4 { font-size: 13px; }
    .markdown-content p {
      margin-bottom: 8px;
      word-wrap: break-word;
      overflow-wrap: break-word;
    }
    .markdown-content ul, .markdown-content ol {
      padding-left: 20px;
      margin-bottom: 8px;
    }
    .markdown-content li {
      margin-bottom: 4px;
    }
    .markdown-content a {
      color: #0078d4;
      text-decoration: none;
    }
    .markdown-content a:hover {
      text-decoration: underline;
    }
    .markdown-content table {
      border-collapse: collapse;
      width: 100%;
      margin-bottom: 8px;
    }
    .markdown-content th, .markdown-content td {
      border: 1px solid rgba(255, 255, 255, 0.2);
      padding: 4px 8px;
      text-align: left;
    }
    .markdown-content img {
      max-width: 100%;
      height: auto;
    }
  `
};
