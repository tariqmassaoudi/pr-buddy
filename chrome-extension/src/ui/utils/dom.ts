import { StyleMap } from './types';

/**
 * Utility functions for DOM manipulation
 */
export const UIUtil = {
  /**
   * Create an element with attributes and styles
   */
  createElement<T extends HTMLElement>(
    tag: string, 
    className?: string, 
    styles?: StyleMap, 
    attributes?: Record<string, string | number>
  ): T {
    const element = document.createElement(tag) as T;
    if (className) element.className = className;
    
    if (styles) {
      Object.entries(styles).forEach(([key, value]) => {
        element.style[key as any] = value;
      });
    }
    
    if (attributes) {
      Object.entries(attributes).forEach(([key, value]) => {
        if (key === 'id') element.id = String(value);
        else if (typeof value === 'number' && key === 'tabIndex') element.tabIndex = value;
        else element.setAttribute(key, String(value));
      });
    }
    
    return element;
  },
  
  /**
   * Append multiple child elements to a parent
   */
  appendChildren(parent: HTMLElement, children: HTMLElement[]): HTMLElement {
    children.forEach(child => parent.appendChild(child));
    return parent;
  },
  
  /**
   * Add styles to document head if not already added
   */
  addStyles(id: string, css: string): void {
    if (!document.getElementById(id)) {
      const style = document.createElement('style');
      style.id = id;
      style.textContent = css;
      document.head.appendChild(style);
    }
  },
  
  /**
   * Find element by ID with type assertion
   */
  getElementById<T extends HTMLElement>(id: string): T | null {
    return document.getElementById(id) as T | null;
  }
};
