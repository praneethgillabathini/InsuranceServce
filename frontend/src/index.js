import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const style = document.createElement('style');
style.textContent = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html, body, #root { height: 100%; overscroll-behavior: none; }

  body {
    background: #f8fafc;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #0f172a;
    -webkit-font-smoothing: antialiased;
  }

  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: #f8fafc; }
  ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #4f46e5, #ec4899); border-radius: 3px; }
  ::selection { background: rgba(79,70,229,0.18); color: #0f172a; }
  button:focus-visible { outline: 2px solid #4f46e5; outline-offset: 2px; }
  button:focus:not(:focus-visible) { outline: none; }

  @keyframes spin     { to { transform: rotate(360deg); } }
  @keyframes pulse    { 0%,100%{opacity:1} 50%{opacity:0.4} }
  @keyframes vpulse   { 0%,100%{transform:scale(1);opacity:.85} 50%{transform:scale(1.08);opacity:1} }
  @keyframes vfadein  { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
  @keyframes emeraldGlow {
    0%,100% { box-shadow: 0 0 16px rgba(79,70,229,0.45); }
    50%      { box-shadow: 0 0 28px rgba(236,72,153,0.4); }
  }

  .app-layout {
    display: grid;
    grid-template-columns: 310px 1fr;
  }

  .sidebar-container {
    border-right: 1px solid #e2e8f0;
  }

  .header-actions {
    display: flex;
  }

  @media (max-width: 900px) {
    .app-layout {
      grid-template-columns: 260px 1fr;
    }
  }

  @media (max-width: 768px) {
    .app-layout {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr;
      overflow: auto;
    }
    .sidebar-container {
      border-right: none;
      border-bottom: 1px solid #e2e8f0;
    }
    .header-actions {
      display: none;
    }
    html, body, #root {
      height: auto;
      min-height: 100vh;
    }
    .main-wrapper {
      height: auto !important;
      overflow: visible !important;
    }
  }
`;
document.head.appendChild(style);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);