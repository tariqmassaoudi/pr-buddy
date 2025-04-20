/**
 * Animation styles and keyframes
 */
export const ANIMATIONS = {
  keyframes: `
    @keyframes rotating {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    
    @keyframes pulse {
      0% { background-color: rgba(0, 120, 212, 0.3); }
      50% { background-color: rgba(0, 120, 212, 0.8); }
      100% { background-color: rgba(0, 120, 212, 0.3); }
    }
    
    .loading-pulse {
      animation: pulse 1.5s infinite;
      background-color: rgba(0, 120, 212, 0.5);
    }
  `,
  styleId: 'animation-styles'
};
