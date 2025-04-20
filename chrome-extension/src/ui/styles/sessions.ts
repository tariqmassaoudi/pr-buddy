/**
 * Styles for session progress indicators
 */
export const SESSION_STYLES = {
  progressIndicator: {
    borderRadius: '4px',
    backgroundColor: 'rgba(0, 0, 0, 0.1)',
    minHeight: '60px',
    position: 'relative',
    overflow: 'hidden',
    width: '100%',
    marginRight: '8px',
    flexShrink: '0'
  },
  loadingIndicator: {
    height: '3px',
    width: '100%',
    position: 'absolute',
    top: '0',
    left: '0',
    borderTopLeftRadius: '4px',
    borderTopRightRadius: '4px'
  },
  stepsTracker: {
    color: 'white',
    paddingLeft: '24px',
    minHeight: '18px',
    lineHeight: '1.4',
    wordWrap: 'break-word'
  }
};
