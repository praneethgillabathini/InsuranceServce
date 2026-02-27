import React, { useCallback, useState } from 'react';

const P1 = '#4f46e5'; const P2 = '#4338ca';
const A1 = '#ec4899'; const S1 = '#0ea5e9';
const GRAD_BTN = `linear-gradient(135deg, ${P1} 0%, ${P2} 100%)`;

export default function Upload({ onProcess, onExtractOnly, isProcessing, shouldGenerateFhir, onFhirToggleChange }) {
  const [file, setFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = useCallback((e) => {
    e.preventDefault(); setIsDragOver(false);
    const f = e.dataTransfer?.files?.[0];
    if (f?.type === 'application/pdf') setFile(f);
  }, []);

  const fmt = (b) => b < 1024 ? `${b} B` : b < 1048576 ? `${(b / 1024).toFixed(1)} KB` : `${(b / 1048576).toFixed(2)} MB`;
  const disabled = !file || isProcessing;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div>
        <div style={{ fontSize: 14, fontWeight: 800, color: '#0f172a', marginBottom: 2 }}>Upload Document</div>
        <div style={{ fontSize: 11, color: '#64748b' }}>Insurance policy PDF — NHCX / IRDAI</div>
      </div>

      <div
        style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: '22px 16px', borderRadius: 16, textAlign: 'center',
          border: `2px ${isDragOver ? 'solid' : 'dashed'} ${isDragOver ? P1 : file ? `${P1}55` : '#e2e8f0'}`,
          background: isDragOver ? '#e0e7ff' : file ? '#f8fafc' : '#ffffff',
          cursor: 'pointer', transition: 'all 0.2s ease', minHeight: 150,
          boxShadow: isDragOver ? `0 0 0 4px rgba(79,70,229,0.12)` : 'none',
        }}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
        onDragLeave={() => setIsDragOver(false)}
        onClick={() => document.getElementById('pdf-input').click()}
      >
        <input id="pdf-input" type="file" accept="application/pdf" style={{ display: 'none' }}
          onChange={e => e.target.files?.[0] && setFile(e.target.files[0])} />

        {file ? (
          <>
            <div style={{
              width: 42, height: 42, borderRadius: 12, marginBottom: 10,
              background: GRAD_BTN, display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: `0 4px 14px rgba(79,70,229,0.35)`,
            }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="white" strokeWidth="1.5" fill="rgba(255,255,255,0.2)" />
                <polyline points="14,2 14,8 20,8" stroke="white" strokeWidth="1.5" fill="none" />
                <line x1="16" y1="13" x2="8" y2="13" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
                <line x1="16" y1="17" x2="8" y2="17" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </div>
            <div style={{ fontSize: 12, fontWeight: 700, color: '#312e81', marginBottom: 2, wordBreak: 'break-all', padding: '0 8px' }}>{file.name}</div>
            <div style={{ fontSize: 10, color: '#64748b' }}>{fmt(file.size)}</div>
            <div style={{ fontSize: 10, color: P1, marginTop: 5, fontWeight: 600 }}>Click to replace</div>
          </>
        ) : (
          <>
            <div style={{ fontSize: 26, marginBottom: 8, opacity: isDragOver ? 1 : 0.5 }}>{isDragOver ? '📂' : '⬆️'}</div>
            <div style={{ fontSize: 13, color: isDragOver ? P2 : '#64748b', fontWeight: isDragOver ? 700 : 400 }}>
              {isDragOver ? 'Release to upload' : 'Drag & drop a PDF'}
            </div>
            <div style={{ fontSize: 11, color: '#d1d5db', marginTop: 3 }}>or click to browse</div>
          </>
        )}
      </div>

      <div style={{
        display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', borderRadius: 12,
        background: shouldGenerateFhir ? '#e0e7ff' : '#f8fafc',
        border: `1px solid ${shouldGenerateFhir ? '#c7d2fe' : '#e2e8f0'}`,
        transition: 'all 0.2s',
      }}>
        <div
          onClick={() => !isProcessing && onFhirToggleChange({ target: { checked: !shouldGenerateFhir } })}
          style={{
            width: 38, height: 21, borderRadius: 11, flexShrink: 0,
            background: shouldGenerateFhir ? GRAD_BTN : '#cbd5e1',
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            position: 'relative', transition: 'all 0.25s',
            boxShadow: shouldGenerateFhir ? '0 0 10px rgba(79,70,229,0.4)' : 'none',
          }}
        >
          <div style={{
            position: 'absolute', width: 15, height: 15, borderRadius: '50%', background: 'white',
            top: 3, left: shouldGenerateFhir ? 20 : 3, transition: 'left 0.22s',
            boxShadow: '0 1px 4px rgba(0,0,0,0.2)',
          }} />
        </div>
        <div>
          <div style={{ fontSize: 12, fontWeight: 600, color: shouldGenerateFhir ? '#312e81' : '#334155', transition: 'color 0.2s' }}>
            Generate FHIR on Upload
          </div>
          <div style={{ fontSize: 10, color: '#64748b' }}>Runs full pipeline immediately</div>
        </div>
      </div>

      <button id="btn-process-claim" onClick={() => onProcess(file)} disabled={disabled} style={{
        padding: '12px 0', borderRadius: 12, border: 'none',
        background: disabled ? '#f1f5f9' : GRAD_BTN,
        color: disabled ? '#94a3b8' : 'white',
        fontSize: 13, fontWeight: 800, cursor: disabled ? 'not-allowed' : 'pointer',
        boxShadow: disabled ? 'none' : '0 4px 18px rgba(79,70,229,0.38)',
        transition: 'all 0.2s',
      }}>
        {isProcessing ? (
          <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
            <span style={{ width: 13, height: 13, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', animation: 'spin 0.65s linear infinite', display: 'inline-block' }} />
            Processing…
          </span>
        ) : '⚡ Process Claim'}
      </button>

    </div>
  );
}