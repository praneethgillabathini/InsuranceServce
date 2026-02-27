import React, { useState, useEffect, useRef } from 'react';
import SummaryCard from './SummaryCard';

const P1 = '#4f46e5'; const P2 = '#4338ca';
const A1 = '#ec4899'; const S1 = '#0ea5e9';
const GRAD_BTN = `linear-gradient(135deg, ${P1} 0%, ${P2} 100%)`;

function JsonViewer({ data }) {
  const hl = JSON.stringify(data, null, 2)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"([^"]+)":/g, `<span style="color:#6ee7b7;font-weight:600">"$1"</span>:`)
    .replace(/: "([^"]*)"/g, `: <span style="color:#fca5a5">"$1"</span>`)
    .replace(/: (\d+\.?\d*)/g, `: <span style="color:#fde68a">$1</span>`)
    .replace(/: (true|false)/g, `: <span style="color:#a5f3fc">$1</span>`)
    .replace(/: (null)/g, `: <span style="color:#94a3b8">$1</span>`);
  return <pre style={{ margin: 0, fontSize: '0.775rem', lineHeight: 1.75, fontFamily: "'JetBrains Mono','Fira Code',monospace", whiteSpace: 'pre-wrap', wordBreak: 'break-all', color: '#e2e8f0' }} dangerouslySetInnerHTML={{ __html: hl }} />;
}

function CopyButton({ data, label = 'Copy' }) {
  const [ok, setOk] = useState(false);
  const go = async () => { try { await navigator.clipboard.writeText(JSON.stringify(data, null, 2)); setOk(true); setTimeout(() => setOk(false), 1800); } catch { } };
  return <button onClick={go} style={{ padding: '4px 11px', borderRadius: 6, cursor: 'pointer', fontSize: 11, fontWeight: 600, border: `1px solid ${ok ? '#a7f3d0' : '#e5e7eb'}`, background: ok ? '#ecfdf5' : '#f9fafb', color: ok ? P2 : '#64748b', transition: 'all 0.15s' }}>{ok ? '✓ Copied' : label}</button>;
}

function DownloadButton({ data, filename = 'output.json' }) {
  const dl = () => { const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })); Object.assign(document.createElement('a'), { href: url, download: filename }).click(); URL.revokeObjectURL(url); };
  return <button onClick={dl} style={{ padding: '4px 11px', borderRadius: 6, cursor: 'pointer', fontSize: 11, fontWeight: 600, border: `1px solid #c7d2fe`, background: '#e0e7ff', color: P2 }}>↓ Download</button>;
}

function TabBtn({ label, active, disabled, onClick, badge }) {
  return (
    <button onClick={onClick} disabled={disabled} style={{
      padding: '9px 14px', borderRadius: '10px 10px 0 0', border: 'none',
      borderBottom: active ? `2px solid ${P1}` : '2px solid transparent',
      background: active ? '#e0e7ff' : 'transparent',
      color: disabled ? '#cbd5e1' : active ? P2 : '#64748b',
      fontSize: 12, fontWeight: active ? 700 : 500, cursor: disabled ? 'not-allowed' : 'pointer',
      transition: 'all 0.15s', display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0,
    }}>
      {label}
      {badge !== undefined && (
        <span style={{ fontSize: 10, padding: '1px 6px', borderRadius: 10, background: active ? '#c7d2fe' : '#f1f5f9', color: active ? P2 : '#64748b' }}>{badge}</span>
      )}
    </button>
  );
}

function LoadingState({ fileName }) {
  const [dots, setDots] = useState(0);
  const msgs = ['🔍 Running OCR on document…', '🤖 Extracting fields with AI…', '⚕️ Mapping to FHIR R4…', '✅ Almost done…'];
  const [mi, setMi] = useState(0);
  useEffect(() => {
    const d = setInterval(() => setDots(x => (x + 1) % 4), 400);
    const m = setInterval(() => setMi(x => Math.min(x + 1, msgs.length - 1)), 3500);
    return () => { clearInterval(d); clearInterval(m); };
  }, []); // eslint-disable-line
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 22 }}>
      <div style={{ position: 'relative', width: 88, height: 88 }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{ position: 'absolute', inset: i * 9, borderRadius: '50%', border: '2px solid transparent', borderTopColor: [P1, P2, A1][i], animation: `spin ${1 + i * 0.3}s linear infinite`, animationDirection: i % 2 === 0 ? 'normal' : 'reverse' }} />
        ))}
        <div style={{ position: 'absolute', inset: 26, borderRadius: '50%', background: GRAD_BTN, opacity: 0.9, animation: 'vpulse 1.5s ease-in-out infinite', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12 }}>⚕</div>
      </div>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 6 }}>
          {fileName}<span style={{ background: GRAD_BTN, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>{'.'.repeat(dots + 1)}</span>
        </div>
        <div style={{ fontSize: 13, color: '#64748b' }}>{msgs[mi]}</div>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: 14 }}>
      <div style={{ width: 72, height: 72, borderRadius: 20, background: 'linear-gradient(135deg, #e0e7ff, #fce7f3)', border: '1px solid #c7d2fe', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 30 }}>📋</div>
      <div style={{ fontSize: 14, color: '#64748b', textAlign: 'center', lineHeight: 1.7 }}>Upload a PDF to see the<br />extracted data and FHIR bundle</div>
    </div>
  );
}

export default function Result({ isProcessing, data, error, fileName, onGenerateFhir, isGeneratingFhir, summary, validation }) {
  const [tab, setTab] = useState(0);
  const scrollRef = useRef(null);
  useEffect(() => { if (!data) { setTab(0); return; } if (data.fhir_bundle) setTab(2); else if (data.extracted_data) setTab(1); }, [data]);
  useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = 0; }, [tab]);

  if (isProcessing) return <LoadingState fileName={fileName} />;
  if (error) return (
    <div style={{ margin: 16, padding: 16, borderRadius: 14, background: '#fce7f3', border: '1px solid #fbcfe8', color: A1, fontSize: 13, display: 'flex', gap: 10, alignItems: 'flex-start', animation: 'vfadein 0.3s ease' }}>
      <span style={{ fontSize: 16, flexShrink: 0 }}>⚠️</span>
      <div><div style={{ fontWeight: 700, marginBottom: 4 }}>Processing Error</div>{error}</div>
    </div>
  );
  if (!data) return <EmptyState />;

  const tabs = [
    { id: 0, label: '✦ Overview' },
    { id: 1, label: '{ } Extracted', disabled: !data.extracted_data, badge: data.extracted_data ? Object.keys(data.extracted_data).length : undefined },
    { id: 2, label: '⚕ FHIR Bundle', disabled: !data.fhir_bundle, badge: data.fhir_bundle ? `${data.fhir_bundle.entry?.length ?? 0}` : undefined },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%', overflow: 'hidden', minHeight: 0 }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', borderBottom: '1px solid #d1fae5', paddingLeft: 8, flexShrink: 0, background: '#ffffff' }}>
        {tabs.map(t => <TabBtn key={t.id} label={t.label} active={tab === t.id} disabled={!!t.disabled} onClick={() => !t.disabled && setTab(t.id)} badge={t.badge} />)}
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 6, paddingBottom: 8, paddingRight: 12, alignItems: 'center' }}>
          {tab === 1 && data.extracted_data && (
            <>
              <CopyButton data={data.extracted_data} label='Copy JSON' />
              <DownloadButton data={data.extracted_data} filename='extracted_data.json' />
              {!data.fhir_bundle && (
                <button id="btn-generate-fhir" onClick={onGenerateFhir} disabled={isGeneratingFhir} style={{ padding: '4px 12px', borderRadius: 7, border: 'none', background: isGeneratingFhir ? '#f3f4f6' : GRAD_BTN, color: isGeneratingFhir ? '#9ca3af' : 'white', fontSize: 11, fontWeight: 800, cursor: isGeneratingFhir ? 'not-allowed' : 'pointer', boxShadow: isGeneratingFhir ? 'none' : '0 3px 12px rgba(16,185,129,0.4)' }}>
                  {isGeneratingFhir ? 'Generating…' : '⚕ Generate FHIR'}
                </button>
              )}
            </>
          )}
          {tab === 2 && data.fhir_bundle && (<><CopyButton data={data.fhir_bundle} label='Copy Bundle' /><DownloadButton data={data.fhir_bundle} filename='fhir_bundle.json' /></>)}
        </div>
      </div>

      <div ref={scrollRef} style={{ flex: 1, minHeight: 0, overflow: 'auto', padding: 16 }}>
        {tab === 0 && (
          <div style={{ animation: 'vfadein 0.25s ease' }}>
            {(summary || validation) ? <SummaryCard summary={summary} validation={validation} /> : (
              <div style={{ padding: 20, borderRadius: 14, background: '#f0fdf4', border: '1px solid #d1fae5', color: '#9ca3af', fontSize: 13, textAlign: 'center' }}>
                {data.fhir_bundle ? 'Summary is being generated…' : 'Generate a FHIR bundle to see the plan summary here.'}
              </div>
            )}
            {data.fhir_bundle?.entry && (
              <div style={{ marginTop: 18 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: '#9ca3af', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 1 }}>Bundle Resources</div>
                {data.fhir_bundle.entry.map((entry, i) => {
                  const r = entry.resource || {};
                  const colors = { InsurancePlan: P1, Organization: S1 };
                  const color = colors[r.resourceType] || '#64748b';
                  return (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px', borderRadius: 10, marginBottom: 5, background: '#ffffff', border: '1px solid #f1f5f9', fontSize: 12, boxShadow: '0 1px 3px rgba(0,0,0,0.04)', animation: `vfadein ${0.1 + i * 0.04}s ease` }}>
                      <span style={{ padding: '2px 8px', borderRadius: 6, background: `${color}12`, color, fontWeight: 700, fontSize: 10, flexShrink: 0 }}>{r.resourceType}</span>
                      <span style={{ color: '#334155', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.name || r.id}</span>
                      <span style={{ color: '#cbd5e1', fontFamily: 'monospace', fontSize: 10, flexShrink: 0 }}>{entry.fullUrl?.replace('urn:uuid:', '').slice(0, 8)}…</span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
        {tab === 1 && (
          <div style={{ borderRadius: 12, background: '#0f172a', border: `1px solid ${P1}22`, padding: 16, animation: 'vfadein 0.2s ease' }}>
            {data.extracted_data ? <JsonViewer data={data.extracted_data} /> : <span style={{ color: '#64748b' }}>No data.</span>}
          </div>
        )}
        {tab === 2 && (
          <div style={{ borderRadius: 12, background: '#0f172a', border: `1px solid ${A1}22`, padding: 16, animation: 'vfadein 0.2s ease' }}>
            {data.fhir_bundle ? <JsonViewer data={data.fhir_bundle} /> : (
              <div style={{ color: '#64748b', fontSize: 13, textAlign: 'center', padding: 40 }}>
                Switch to <strong style={{ color: '#c7d2fe' }}>{ } Extracted</strong> and click <strong style={{ color: A1 }}>⚕ Generate FHIR</strong>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}