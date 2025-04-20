/**
 * Styles for the panel component
 */
export const PANEL_STYLES = {
  // Common panel styles
  panelStyles: {
    display: 'none',
    position: 'relative',
    maxHeight: '600px',
    margin: '16px 0',
    overflowY: 'auto',
    overflowX: 'hidden'
  },
  // Content area styles
  contentStyles: {
    display: 'flex',
    flexDirection: 'column',
    minHeight: '300px',
    height: 'auto',
    maxHeight: '550px',
    position: 'relative',
    overflow: 'hidden'
  },
  // Tool calls container styles
  toolCallsContainerStyles: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    position: 'relative',
    gap: '8px'
  },
  // Header styles
  headerStyles: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px'
  },
  // Close button styles
  closeButtonStyles: {
    padding: '4px',
    minWidth: 'auto',
    backgroundColor: 'transparent',
    border: 'none'
  },
  // Tool calls list styles
  toolCallsListStyles: {
    paddingBottom: '60px',
    overflowY: 'auto',
    maxHeight: '450px',
    minHeight: '200px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  }
};
