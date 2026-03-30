/**
 * @module LoadingDots
 * @description Animated typing indicator ("...") used inside loading states.
 * Each dot is wrapped in a separate span and animated via the CSS
 * "typing-blink" keyframes defined in App.css.
 *
 * @component
 */
import React from 'react';

const LoadingDots = () => (
  <span className="typing-dots" style={{ letterSpacing: '1px' }}>
    <span>.</span><span>.</span><span>.</span>
  </span>
);

export default LoadingDots;
