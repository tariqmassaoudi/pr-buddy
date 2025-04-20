/**
 * Status colors and icons for different states
 */
export const STATUS_COLORS = {
  success: 'rgba(16, 124, 16, 0.2)',  // Green for success
  error: 'rgba(168, 0, 0, 0.2)',      // Red for errors
  default: 'rgba(0, 0, 0, 0.1)'       // Default background
};

/**
 * HTML templates for status icons
 */
export const ICONS = {
  success: '<span class="fluent-icons-enabled"><span aria-hidden="true" class="flex-noshrink fabric-icon ms-Icon--CheckMark small" style="color: white;"></span></span>',
  error: '<span class="fluent-icons-enabled"><span aria-hidden="true" class="flex-noshrink fabric-icon ms-Icon--Error small" style="color: white;"></span></span>',
  warning: '<span class="fluent-icons-enabled"><span aria-hidden="true" class="flex-noshrink fabric-icon ms-Icon--Warning small" style="color: #a80000;"></span></span>'
};
