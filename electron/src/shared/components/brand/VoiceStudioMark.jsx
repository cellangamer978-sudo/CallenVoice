import React from 'react';

/**
 * CallenVoice mark: an open "C" (the original voice) with an orange waveform
 * leaving through its opening (the same voice in another language). Same
 * geometry as branding/logo.svg, without the tile, for titlebar sizes.
 * The component keeps its upstream name so imports stay stable.
 */
export default function VoiceStudioMark({ className = '', title, ...props }) {
  return (
    <svg
      viewBox="0 0 64 64"
      fill="none"
      className={className}
      role={title ? 'img' : undefined}
      aria-hidden={title ? undefined : true}
      {...props}
    >
      {title ? <title>{title}</title> : null}
      <path
        d="M37.8 21.8 A15.9 15.9 0 1 0 37.8 42.2"
        stroke="currentColor"
        strokeWidth="6.5"
        strokeLinecap="round"
      />
      <g fill="var(--primary, #FF6A00)">
        <rect x="35.4" y="28.3" width="3.5" height="7.5" rx="1.75" />
        <rect x="41.4" y="23.3" width="3.5" height="17.5" rx="1.75" />
        <rect x="47.4" y="26.4" width="3.5" height="11.2" rx="1.75" />
        <rect x="53.4" y="30.1" width="3.5" height="3.8" rx="1.75" />
      </g>
    </svg>
  );
}
